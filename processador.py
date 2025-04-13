import streamlit as st
import polars as pl
import time
from io import BytesIO, StringIO
import pyarrow.parquet as pq
import pyarrow as pa
import csv

# Configurar a página
st.set_page_config(page_title="Processador de Arquivos", layout="centered")

st.title("Processador de Arquivos")

st.html("""
<style>
div[data-testid="stFileUploader"]>section[data-testid="stFileUploaderDropzone"]>button[data-testid="stBaseButton-secondary"] {
    text-indent: -9999px;
    line-height: 0;
}
div[data-testid="stFileUploader"]>section[data-testid="stFileUploaderDropzone"]>button[data-testid="stBaseButton-secondary"]::after {
    line-height: initial;
    content: "Buscar Arquivos";
    text-indent: 0;
}
div[data-testid="stFileUploaderDropzoneInstructions"]>div>span {
    visibility:hidden;
}
div[data-testid="stFileUploaderDropzoneInstructions"]>div>span::after {
    content:"Arraste arquivos aqui";
    visibility:visible;
    display:block;
}
div[data-testid="stFileUploaderDropzoneInstructions"]>div>small {
    visibility:hidden;
}
div[data-testid=stFileUploaderDropzoneInstructions]>div>small::before {
    content:"Limite de 5GB por arquivo";
    visibility:visible;
    display:block;
}
</style>
""")

@st.cache_data(show_spinner=False)
def load_data(file, file_type):
    if file_type == "csv":
        file_content = file.read()
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        delimiters = [';', ',', '\t', '|']

        for encoding in encodings:
            try:
                str_content = file_content.decode(encoding)
                for delimiter in delimiters:
                    try:
                        df = pl.read_csv(StringIO(str_content), separator=delimiter)
                        if df.shape[1] > 1:
                            return df
                    except:
                        continue
            except:
                continue

        st.error("Não foi possível ler o arquivo CSV. Verifique encoding e delimitador.")
        return None

    elif file_type == "xlsx":
        try:
            return pl.read_excel(file)
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {e}")
            return None

    return None

@st.cache_data(show_spinner=False)
def convert_to_parquet(_df: pl.DataFrame):
    table = pa.Table.from_pandas(_df.to_pandas())
    buffer = BytesIO()
    pq.write_table(table, buffer)
    buffer.seek(0)
    return buffer

# Inicializar session_state
if 'df' not in st.session_state:
    st.session_state.df = None
if 'df_parquet' not in st.session_state:
    st.session_state.df_parquet = None
if 'processed_result' not in st.session_state:
    st.session_state.processed_result = None
if 'file_type' not in st.session_state:
    st.session_state.file_type = None
if 'current_file_hash' not in st.session_state:
    st.session_state.current_file_hash = None

uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV ou XLSX", type=["csv", "xlsx"])

if uploaded_file is not None:
    file_hash = hash(uploaded_file.read())
    uploaded_file.seek(0)

    if st.session_state.df is None or st.session_state.current_file_hash != file_hash:
        with st.spinner("Lendo o arquivo, por favor aguarde..."):
            file_type = uploaded_file.name.split(".")[-1]
            df = load_data(uploaded_file, file_type)

            if df is not None:
                parquet_buffer = convert_to_parquet(df)
                df_parquet = pl.read_parquet(parquet_buffer)

                st.session_state.df = df
                st.session_state.df_parquet = df_parquet
                st.session_state.file_type = file_type
                st.session_state.current_file_hash = file_hash

                success_message = st.success("Arquivo carregado com sucesso!")
                time.sleep(3)
                success_message.empty()

if st.session_state.df is not None:
    df = st.session_state.df
    df_parquet = st.session_state.df_parquet

    st.info(f"""
        📊 **Informações do arquivo:**
        - Total de linhas: {df.shape[0]}
        - Total de colunas: {df.shape[1]}
    """)

    st.warning("⚠️ Mostrando as 5 primeiras linhas para referência.")
    st.dataframe(df.head().to_pandas())

    st.sidebar.header("Configurações do processamento")
    colunas_disponiveis = df_parquet.columns

    colunas_selecionadas = st.sidebar.multiselect(
        "Selecione as colunas que deseja manter:",
        options=colunas_disponiveis,
        default=colunas_disponiveis
    )

    coluna_data = st.sidebar.selectbox("Coluna de data para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
    if coluna_data != "Nenhuma":
        try:
            datas = df_parquet[coluna_data].cast(pl.Datetime)
            data_inicio = st.sidebar.date_input("Data de início", value=datas.min().date())
            data_fim = st.sidebar.date_input("Data de fim", value=datas.max().date())
        except:
            st.sidebar.warning("Coluna selecionada não pôde ser interpretada como data.")

    coluna_valor = st.sidebar.selectbox("Coluna numérica para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
    if coluna_valor != "Nenhuma":
        valor_min = float(df_parquet[coluna_valor].min())
        valor_max = float(df_parquet[coluna_valor].max())
        valor_min_input = st.sidebar.number_input("Valor mínimo", value=valor_min)
        valor_max_input = st.sidebar.number_input("Valor máximo", value=valor_max)

    coluna_texto = st.sidebar.selectbox("Coluna de texto para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
    if coluna_texto != "Nenhuma":
        texto_filtro = st.sidebar.text_input("Texto para filtrar")

    coluna_categoria = st.sidebar.selectbox("Coluna de categoria para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
    if coluna_categoria != "Nenhuma":
        categorias = df_parquet[coluna_categoria].unique().to_list()
        categorias_selecionadas = st.sidebar.multiselect("Selecione as categorias:", options=categorias)

    realizar_agrupamento = st.sidebar.checkbox("Realizar agrupamento?", value=True)

    if colunas_selecionadas:
        if realizar_agrupamento:
            coluna_agrupamento = st.sidebar.selectbox("Coluna para agrupamento:", options=colunas_selecionadas)
            coluna_operacao = st.sidebar.selectbox("Coluna para operação:", options=[c for c in colunas_selecionadas if c != coluna_agrupamento])
            operacao = st.sidebar.radio("Operação:", options=["Soma", "Contagem"])

        if st.sidebar.button("Processar"):
            st.write("Processando os dados...")
            progress_bar = st.progress(0)

            df_filtrado = df_parquet

            if coluna_data != "Nenhuma":
                df_filtrado = df_filtrado.filter(
                    (pl.col(coluna_data).cast(pl.Date) >= pl.lit(data_inicio)) &
                    (pl.col(coluna_data).cast(pl.Date) <= pl.lit(data_fim))
                )
            if coluna_valor != "Nenhuma":
                df_filtrado = df_filtrado.filter(
                    (pl.col(coluna_valor) >= valor_min_input) &
                    (pl.col(coluna_valor) <= valor_max_input)
                )
            if coluna_texto != "Nenhuma" and texto_filtro:
                df_filtrado = df_filtrado.filter(
                    pl.col(coluna_texto).cast(str).str.contains(texto_filtro, literal=True)
                )
            if coluna_categoria != "Nenhuma":
                df_filtrado = df_filtrado.filter(
                    pl.col(coluna_categoria).is_in(categorias_selecionadas)
                )

            for etapa in range(5):
                time.sleep(0.3)
                progress_bar.progress((etapa + 1) / 5)

            if realizar_agrupamento:
                if operacao == "Soma":
                    resultado = df_filtrado.select([coluna_agrupamento, coluna_operacao]) \
                        .groupby(coluna_agrupamento).agg(pl.col(coluna_operacao).sum().alias("Soma"))
                else:
                    resultado = df_filtrado.select([coluna_agrupamento, coluna_operacao]) \
                        .groupby(coluna_agrupamento).agg(pl.col(coluna_operacao).n_unique().alias("Contagem"))
            else:
                resultado = df_filtrado.select(colunas_selecionadas)

            st.session_state.processed_result = resultado
            st.success("Processamento concluído!")
            st.dataframe(resultado.to_pandas())

            if st.session_state.file_type == "csv":
                st.download_button(
                    label="Baixar CSV",
                    data=resultado.write_csv(),
                    file_name="resultado.csv",
                    mime="text/csv"
                )
            else:
                output = BytesIO()
                resultado.to_pandas().to_excel(output, index=False, engine="openpyxl")
                st.download_button(
                    label="Baixar XLSX",
                    data=output.getvalue(),
                    file_name="resultado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

# Remover o arquivo da memória quando o usuário clicar no "x"
if uploaded_file is None and 'df' in st.session_state:
    # Verifica se realmente há um arquivo carregado para remover
    if st.session_state.df is not None:
        del st.session_state.df
        del st.session_state.df_parquet
        del st.session_state.processed_result
        del st.session_state.file_type
        del st.session_state.current_file_hash
        
        # Remover também os filtros e seleções da sidebar
        keys_to_clear = [
            "colunas_selecionadas", "coluna_data", "data_inicio", "data_fim",
            "coluna_valor", "valor_min", "valor_max",
            "coluna_texto", "texto_filtro",
            "coluna_categoria", "categorias_selecionadas",
            "coluna_agrupamento", "coluna_operacao", "operacao",
            "realizar_agrupamento"
        ]
        for key in keys_to_clear:
            if key in st.session_state:
                del st.session_state[key]

        # Exibe a mensagem de sucesso e força recarregamento
        st.success("Arquivo removido com sucesso.")
        st.rerun()
