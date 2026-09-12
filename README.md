# Mini-Projeto de Análise Exploratória da Base Varejo

**Autor:** Ednelson Rocha da Silva  
**Turma:** Analise_de_Dados_T6  
**Disciplina:** Análise de Dados com Python - Módulo 1, Semana 07

## Objetivo

O projeto transforma a Base Varejo bruta em uma versão consistente para análise. O script identifica problemas, limpa texto e tipos, trata categorias ausentes, elimina duplicatas exatas, calcula estatísticas do número de filhos e compara vendas por gênero, categoria e mês.

## Particularidade da análise

Cada linha representa um item, e não uma compra completa. Por isso, `CO_ID` pode aparecer várias vezes. A análise distingue itens vendidos, compras únicas e itens por compra. Como não há coluna de preço ou valor, “vendas” significa volume de itens ou compras, não faturamento.

## Estrutura

```text
.
├── Base Varejo.csv
├── Miniprojeto_Varejo_Ednelson_Rocha_da_Silva.py
├── Miniprojeto_Varejo_Ednelson_Rocha_da_Silva.ipynb
├── README.md
├── README_EdnelsonRochaDaSilva_Analise_de_Dados_T6.md
├── requirements.txt
└── saidas/
    ├── df_limpo.csv
    ├── relatorio_resultados.txt
    ├── itens_por_genero.csv
    ├── compras_por_genero.csv
    ├── categorias.csv
    └── serie_mensal.csv
```

## Como executar no VS Code

```powershell
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
python Miniprojeto_Varejo_Ednelson_Rocha_da_Silva.py
```

Ao terminar, consulte a pasta `saidas`. Os arquivos de saída são atualizados a cada execução.

## Qualidade e limpeza

- 830.000 registros e 10 colunas úteis na origem.
- Quatro colunas excedentes totalmente vazias foram descartadas.
- 96.553 linhas exatamente duplicadas foram removidas.
- 3.650 categorias vazias ou `#N/D` foram classificadas como `NAO_INFORMADA`.
- Datas foram convertidas para `datetime`.

## Principais conclusões

1. O gênero feminino concentra o maior volume, com 382.427 itens.
2. ALIMENTOS é a categoria líder, com 384.197 itens.
3. Outubro de 2021 apresenta o maior volume mensal, com 28.575 itens.
4. Cada compra contém, em média, 39,71 linhas de item após a limpeza.
5. Não é possível analisar faturamento porque a base não contém preço ou valor.

## Repositório

Nome exigido: `Miniprojeto_EdnelsonRochaDaSilva_Analise_de_Dados_T6`
