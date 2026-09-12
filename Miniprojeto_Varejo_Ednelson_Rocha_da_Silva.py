"""Mini-Projeto Avaliativo - Análise de Dados com Python [T6].

Autor: Ednelson Rocha da Silva
Turma: Analise_de_Dados_T6

Executa uma AED reprodutível da Base Varejo e grava os resultados em saidas/.
Cada linha representa um item; CO_ID identifica a compra que pode ocupar várias linhas.
"""

from pathlib import Path
import re
import pandas as pd

PASTA_PROJETO = Path(__file__).resolve().parent
ARQUIVO_ENTRADA = PASTA_PROJETO / "Base Varejo.csv"
PASTA_SAIDAS = PASTA_PROJETO / "saidas"
ARQUIVO_LIMPO = PASTA_SAIDAS / "df_limpo.csv"
ARQUIVO_RELATORIO = PASTA_SAIDAS / "relatorio_resultados.txt"


def padronizar_nome_coluna(nome: str) -> str:
    """Remove espaços e símbolos inesperados dos nomes das colunas."""
    return re.sub(r"[^A-Z0-9_]+", "_", str(nome).strip().upper()).strip("_")


def carregar_base(caminho: Path) -> pd.DataFrame:
    """Carrega o CSV no padrão brasileiro e remove colunas totalmente vazias."""
    if not caminho.exists():
        raise FileNotFoundError(
            f"Base não encontrada em: {caminho}\n"
            "Copie 'Base Varejo.csv' para a mesma pasta deste script."
        )
    df = pd.read_csv(
        caminho,
        sep=";",
        encoding="utf-8-sig",
        dtype="string",
        low_memory=False,
    )
    df.columns = [padronizar_nome_coluna(c) for c in df.columns]
    # O arquivo original possui campos excedentes vazios após PR_NOME.
    df = df.dropna(axis=1, how="all")
    return df


def diagnosticar(df: pd.DataFrame) -> dict:
    """Mede problemas antes da limpeza sem alterar a base."""
    categorias_invalidas = (
        df["PR_CAT"].fillna("").str.strip().str.upper().isin(["", "#N/D", "N/A", "NA"])
    )
    datas_convertidas = pd.to_datetime(df["DATA"], format="%d/%m/%Y", errors="coerce")
    return {
        "linhas": len(df),
        "colunas": len(df.columns),
        "nulos_por_coluna": df.isna().sum(),
        "duplicatas_exatas": int(df.duplicated().sum()),
        "categorias_invalidas": int(categorias_invalidas.sum()),
        "datas_invalidas": int(datas_convertidas.isna().sum()),
    }


def limpar_base(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    """Padroniza texto/tipos, trata categoria ausente e remove duplicatas exatas.

    A categoria ausente é imputada como 'NAO_INFORMADA' porque excluir a linha
    apagaria um item real da compra. Linhas sem identificadores essenciais são
    removidas, pois não podem ser ligadas com segurança a compra, cliente ou produto.
    """
    limpo = df.copy()
    colunas_texto = ["CL_GENERO", "CL_SEG", "PR_CAT", "PR_NOME"]
    for coluna in colunas_texto:
        limpo[coluna] = limpo[coluna].str.strip().str.upper()

    marcadores_ausencia = {"": pd.NA, "#N/D": pd.NA, "N/A": pd.NA, "NA": pd.NA}
    limpo["PR_CAT"] = limpo["PR_CAT"].replace(marcadores_ausencia).fillna("NAO_INFORMADA")
    limpo["DATA"] = pd.to_datetime(limpo["DATA"], format="%d/%m/%Y", errors="coerce")

    colunas_inteiras = ["CO_ID", "CL_ID", "CL_EC", "CL_FHL", "PR_ID"]
    for coluna in colunas_inteiras:
        limpo[coluna] = pd.to_numeric(limpo[coluna], errors="coerce").astype("Int64")

    antes = len(limpo)
    limpo = limpo.drop_duplicates()
    duplicatas_removidas = antes - len(limpo)

    essenciais = ["DATA", "CO_ID", "CL_ID", "PR_ID", "PR_NOME"]
    antes_essenciais = len(limpo)
    limpo = limpo.dropna(subset=essenciais)
    linhas_essenciais_removidas = antes_essenciais - len(limpo)

    # Número de filhos ausente é preservado como nulo: imputar a média distorceria
    # a distribuição solicitada. As estatísticas usam apenas respostas válidas.
    filhos_invalidos = limpo["CL_FHL"].notna() & (limpo["CL_FHL"] < 0)
    filhos_negativos_corrigidos = int(filhos_invalidos.sum())
    limpo.loc[filhos_invalidos, "CL_FHL"] = pd.NA

    return limpo, {
        "duplicatas_removidas": duplicatas_removidas,
        "linhas_essenciais_removidas": linhas_essenciais_removidas,
        "filhos_negativos_convertidos_em_nulo": filhos_negativos_corrigidos,
    }


def calcular_analises(df: pd.DataFrame) -> dict:
    """Calcula estatísticas no nível correto de item, compra e cliente."""
    filhos_por_cliente = df[["CL_ID", "CL_FHL"]].dropna().drop_duplicates("CL_ID")["CL_FHL"]
    estatisticas_filhos = filhos_por_cliente.describe(percentiles=[0.25, 0.50, 0.75])
    estatisticas_filhos.loc["mediana"] = filhos_por_cliente.median()
    modas = filhos_por_cliente.mode().tolist()

    # Itens vendidos por gênero: contagem de linhas, coerente com o grão da base.
    itens_por_genero = (
        df.assign(CL_GENERO=df["CL_GENERO"].fillna("NAO_INFORMADO"))
        .groupby("CL_GENERO", dropna=False)
        .size()
        .sort_values(ascending=False)
        .rename("ITENS_VENDIDOS")
    )
    compras_por_genero = (
        df.assign(CL_GENERO=df["CL_GENERO"].fillna("NAO_INFORMADO"))
        .groupby("CL_GENERO", dropna=False)["CO_ID"]
        .nunique()
        .sort_values(ascending=False)
        .rename("COMPRAS_UNICAS")
    )
    categorias = (
        df.groupby("PR_CAT", dropna=False)
        .agg(ITENS_VENDIDOS=("PR_ID", "size"), COMPRAS_UNICAS=("CO_ID", "nunique"))
        .sort_values("ITENS_VENDIDOS", ascending=False)
    )
    compras = df.groupby("CO_ID").agg(ITENS_POR_COMPRA=("PR_ID", "size"), CLIENTES=("CL_ID", "nunique"))
    serie_mensal = df.groupby(df["DATA"].dt.to_period("M")).agg(
        ITENS_VENDIDOS=("PR_ID", "size"), COMPRAS_UNICAS=("CO_ID", "nunique")
    )
    return {
        "filhos": estatisticas_filhos,
        "modas_filhos": modas,
        "itens_genero": itens_por_genero,
        "compras_genero": compras_por_genero,
        "categorias": categorias,
        "compras": compras,
        "mensal": serie_mensal,
    }


def montar_conclusoes(df: pd.DataFrame, diagnostico: dict, analises: dict) -> list[str]:
    """Gera conclusões diretamente dos resultados observados."""
    genero_itens = analises["itens_genero"].index[0]
    categoria = analises["categorias"].index[0]
    mes = str(analises["mensal"]["ITENS_VENDIDOS"].idxmax())
    media_itens = analises["compras"]["ITENS_POR_COMPRA"].mean()
    return [
        f"O gênero com maior volume de itens é {genero_itens}, com {analises['itens_genero'].iloc[0]:,} itens.",
        f"A categoria líder é {categoria}, com {analises['categorias'].iloc[0]['ITENS_VENDIDOS']:,.0f} itens.",
        f"O mês de maior volume é {mes}, com {analises['mensal'].loc[analises['mensal']['ITENS_VENDIDOS'].idxmax(), 'ITENS_VENDIDOS']:,} itens.",
        f"Cada compra possui em média {media_itens:.2f} itens; CO_ID foi agrupado para não confundir item com compra.",
        f"A base original tinha {diagnostico['duplicatas_exatas']:,} duplicatas exatas e {diagnostico['categorias_invalidas']:,} categorias ausentes/sentinela.",
        "A base não contém preço/valor/quantidade; portanto, 'vendas' significa volume de itens e compras, não faturamento.",
    ]


def salvar_resultados(df: pd.DataFrame, tipos_originais: pd.Series, diagnostico: dict, limpeza: dict, analises: dict, conclusoes: list[str]) -> None:
    """Exporta base limpa, tabelas agregadas e relatório textual."""
    PASTA_SAIDAS.mkdir(exist_ok=True)
    df.to_csv(ARQUIVO_LIMPO, index=False, encoding="utf-8-sig", date_format="%Y-%m-%d")
    analises["itens_genero"].to_csv(PASTA_SAIDAS / "itens_por_genero.csv", encoding="utf-8-sig")
    analises["compras_genero"].to_csv(PASTA_SAIDAS / "compras_por_genero.csv", encoding="utf-8-sig")
    analises["categorias"].to_csv(PASTA_SAIDAS / "categorias.csv", encoding="utf-8-sig")
    analises["mensal"].to_csv(PASTA_SAIDAS / "serie_mensal.csv", encoding="utf-8-sig")

    secoes = [
        "MINI-PROJETO - ANÁLISE EXPLORATÓRIA DA BASE VAREJO",
        "Autor: Ednelson Rocha da Silva | Turma: Analise_de_Dados_T6",
        "",
        "1. PERFIL DA BASE ORIGINAL",
        f"Registros: {diagnostico['linhas']:,} | Colunas úteis: {diagnostico['colunas']}",
        f"Tipos originais:\n{tipos_originais.to_string()}",
        f"Nulos por coluna (antes da limpeza):\n{diagnostico['nulos_por_coluna'].to_string()}",
        f"Duplicatas exatas: {diagnostico['duplicatas_exatas']:,}",
        f"Categorias ausentes/#N/D: {diagnostico['categorias_invalidas']:,}",
        f"Datas inválidas: {diagnostico['datas_invalidas']:,}",
        "",
        "2. LIMPEZA REALIZADA",
        "Categoria vazia/#N/D → NAO_INFORMADA (preserva o item comprado).",
        "Datas → datetime; identificadores e número de filhos → Int64.",
        "Duplicatas exatas removidas; linhas sem chaves essenciais removidas.",
        str(limpeza),
        "",
        "3. ESTATÍSTICAS - NÚMERO DE FILHOS (um registro por cliente)",
        analises["filhos"].to_string(),
        f"Moda(s): {analises['modas_filhos']}",
        "",
        "4. AGRUPAMENTOS",
        f"Itens por gênero:\n{analises['itens_genero'].to_string()}",
        f"Compras únicas por gênero:\n{analises['compras_genero'].to_string()}",
        f"Top 10 categorias:\n{analises['categorias'].head(10).to_string()}",
        f"Série mensal:\n{analises['mensal'].to_string()}",
        "",
        "5. CONCLUSÕES",
        *[f"- {texto}" for texto in conclusoes],
    ]
    ARQUIVO_RELATORIO.write_text("\n".join(secoes), encoding="utf-8")


def main() -> None:
    print("1/5 - Carregando a base...")
    bruto = carregar_base(ARQUIVO_ENTRADA)
    print(f"Registros: {len(bruto):,} | Colunas úteis: {len(bruto.columns)}")
    print("\nColunas e tipos originais:\n", bruto.dtypes)
    print("2/5 - Diagnosticando qualidade...")
    diagnostico = diagnosticar(bruto)
    print("Nulos por coluna:\n", diagnostico["nulos_por_coluna"])
    print("3/5 - Limpando dados...")
    limpo, resumo_limpeza = limpar_base(bruto)
    print("4/5 - Calculando estatísticas e agrupamentos...")
    analises = calcular_analises(limpo)
    conclusoes = montar_conclusoes(limpo, diagnostico, analises)
    print("5/5 - Salvando entregáveis...")
    salvar_resultados(limpo, bruto.dtypes, diagnostico, resumo_limpeza, analises, conclusoes)
    print("\nCONCLUSÕES")
    for texto in conclusoes:
        print("-", texto)
    print(f"\nConcluído. Resultados em: {PASTA_SAIDAS}")


if __name__ == "__main__":
    main()
