"""Sistema de Controle de Estoque (linha de comando).

Cadastro de produtos, entrada e saída de mercadoria, alerta de estoque
baixo e relatório com o valor total em estoque. Os dados ficam salvos
em um arquivo JSON, então nada se perde ao fechar o programa.
"""

import json
from datetime import datetime
from pathlib import Path

ARQUIVO = Path(__file__).with_name("estoque.json")


class Produto:
    def __init__(self, codigo, nome, preco, quantidade=0, minimo=5):
        self.codigo = codigo
        self.nome = nome
        self.preco = float(preco)
        self.quantidade = int(quantidade)
        self.minimo = int(minimo)

    @property
    def valor_total(self):
        return self.preco * self.quantidade

    @property
    def estoque_baixo(self):
        return self.quantidade <= self.minimo

    def para_dict(self):
        return vars(self).copy()


class Estoque:
    def __init__(self, arquivo=ARQUIVO):
        self.arquivo = Path(arquivo)
        self.produtos = {}
        self.movimentacoes = []
        self.carregar()

    # ---------- persistência ----------
    def carregar(self):
        if not self.arquivo.exists():
            return
        dados = json.loads(self.arquivo.read_text(encoding="utf-8"))
        self.produtos = {p["codigo"]: Produto(**p) for p in dados.get("produtos", [])}
        self.movimentacoes = dados.get("movimentacoes", [])

    def salvar(self):
        dados = {
            "produtos": [p.para_dict() for p in self.produtos.values()],
            "movimentacoes": self.movimentacoes,
        }
        self.arquivo.write_text(json.dumps(dados, ensure_ascii=False, indent=2), encoding="utf-8")

    # ---------- operações ----------
    def cadastrar(self, codigo, nome, preco, minimo=5):
        if codigo in self.produtos:
            raise ValueError(f"Já existe produto com o código {codigo}.")
        if float(preco) < 0:
            raise ValueError("O preço não pode ser negativo.")
        self.produtos[codigo] = Produto(codigo, nome, preco, 0, minimo)
        self.salvar()

    def buscar(self, codigo):
        produto = self.produtos.get(codigo)
        if produto is None:
            raise KeyError(f"Produto {codigo} não encontrado.")
        return produto

    def entrada(self, codigo, quantidade):
        self._movimentar(codigo, quantidade, "entrada")

    def saida(self, codigo, quantidade):
        self._movimentar(codigo, quantidade, "saida")

    def _movimentar(self, codigo, quantidade, tipo):
        quantidade = int(quantidade)
        if quantidade <= 0:
            raise ValueError("A quantidade precisa ser maior que zero.")
        produto = self.buscar(codigo)
        if tipo == "saida":
            if quantidade > produto.quantidade:
                raise ValueError(
                    f"Estoque insuficiente: há {produto.quantidade} unidade(s) de {produto.nome}."
                )
            produto.quantidade -= quantidade
        else:
            produto.quantidade += quantidade
        self.movimentacoes.append({
            "data": datetime.now().strftime("%d/%m/%Y %H:%M"),
            "codigo": codigo,
            "tipo": tipo,
            "quantidade": quantidade,
        })
        self.salvar()

    def remover(self, codigo):
        self.buscar(codigo)
        del self.produtos[codigo]
        self.salvar()

    def em_falta(self):
        return [p for p in self.produtos.values() if p.estoque_baixo]

    def valor_total(self):
        return sum(p.valor_total for p in self.produtos.values())


# ---------- interface no terminal ----------
def moeda(valor):
    return f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def listar(estoque):
    if not estoque.produtos:
        print("\nNenhum produto cadastrado.")
        return
    print(f"\n{'CÓD':<8}{'PRODUTO':<25}{'QTD':>6}{'PREÇO':>14}{'TOTAL':>16}")
    print("-" * 69)
    for p in sorted(estoque.produtos.values(), key=lambda p: p.nome):
        alerta = "  ⚠ baixo" if p.estoque_baixo else ""
        print(f"{p.codigo:<8}{p.nome[:24]:<25}{p.quantidade:>6}{moeda(p.preco):>14}{moeda(p.valor_total):>16}{alerta}")
    print("-" * 69)
    print(f"{'Valor total em estoque:':<53}{moeda(estoque.valor_total()):>16}")


def pedir(texto):
    return input(texto).strip()


def menu():
    estoque = Estoque()
    opcoes = {
        "1": "Listar produtos",
        "2": "Cadastrar produto",
        "3": "Registrar entrada",
        "4": "Registrar saída",
        "5": "Produtos com estoque baixo",
        "6": "Histórico de movimentações",
        "7": "Remover produto",
        "0": "Sair",
    }
    while True:
        print("\n===== CONTROLE DE ESTOQUE =====")
        for chave, texto in opcoes.items():
            print(f"[{chave}] {texto}")
        escolha = pedir("Escolha: ")
        try:
            if escolha == "1":
                listar(estoque)
            elif escolha == "2":
                estoque.cadastrar(
                    pedir("Código: ").upper(),
                    pedir("Nome: "),
                    pedir("Preço (ex: 12.50): ").replace(",", "."),
                    pedir("Estoque mínimo [5]: ") or 5,
                )
                print("Produto cadastrado.")
            elif escolha == "3":
                estoque.entrada(pedir("Código: ").upper(), pedir("Quantidade: "))
                print("Entrada registrada.")
            elif escolha == "4":
                estoque.saida(pedir("Código: ").upper(), pedir("Quantidade: "))
                print("Saída registrada.")
            elif escolha == "5":
                faltando = estoque.em_falta()
                if not faltando:
                    print("\nNenhum produto com estoque baixo.")
                for p in faltando:
                    print(f"⚠ {p.nome}: {p.quantidade} unidade(s) (mínimo {p.minimo})")
            elif escolha == "6":
                if not estoque.movimentacoes:
                    print("\nNenhuma movimentação ainda.")
                for m in estoque.movimentacoes[-20:]:
                    sinal = "+" if m["tipo"] == "entrada" else "-"
                    print(f"{m['data']}  {m['codigo']:<8} {sinal}{m['quantidade']}")
            elif escolha == "7":
                estoque.remover(pedir("Código: ").upper())
                print("Produto removido.")
            elif escolha == "0":
                print("Até mais!")
                break
            else:
                print("Opção inválida.")
        except (ValueError, KeyError) as erro:
            print(f"Erro: {erro.args[0]}")


if __name__ == "__main__":
    menu()
