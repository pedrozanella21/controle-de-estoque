# Controle de Estoque 📦

Sistema de controle de estoque em Python, feito para rodar no terminal.

A ideia veio da minha experiência trabalhando com reposição, recebimento de mercadoria e estoque no varejo: registrar o que entra e o que sai, saber o que está acabando e quanto dinheiro está parado na prateleira.

## Funcionalidades

- Cadastro de produtos com código, nome, preço e estoque mínimo
- Entrada e saída de mercadoria (não deixa vender mais do que tem)
- Alerta de estoque baixo
- Histórico das movimentações com data e hora
- Relatório com o valor total em estoque
- Dados salvos em `estoque.json`, nada se perde ao fechar

## Como rodar

Precisa do Python 3.8 ou mais novo. Não usa nenhuma biblioteca externa.

```bash
python estoque.py
```

## Exemplo

```
CÓD     PRODUTO                     QTD         PREÇO           TOTAL
---------------------------------------------------------------------
P002    Adubo NPK 1kg                 3      R$ 22,90        R$ 68,70  ⚠ baixo
P001    Ração Bovina 40kg            12      R$ 89,90     R$ 1.078,80
---------------------------------------------------------------------
Valor total em estoque:                                   R$ 1.147,50
```

## Conceitos usados

- Programação orientada a objetos (classes `Produto` e `Estoque`, `@property`)
- Tratamento de erros com exceções
- Leitura e escrita de JSON
- Organização do código separando regra de negócio da interface
