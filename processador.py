import streamlit as st
import pandas as pd
import time
from io import BytesIO
import pyarrow.parquet as pq
import pyarrow as pa
import csv

# Configurar a página
st.set_page_config(page_title="Processador de Arquivos", layout="centered")

st.title("Processador de Arquivos")

st.html(
"""
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
"""
)

# Função para carregar dados a partir do arquivo CSV ou XLSX
@st.cache_data
def load_data(file, file_type):
    if file_type == "csv":
        # Detectar automaticamente o delimitador
        file_content = file.getvalue().decode("utf-8")
        sniffer = csv.Sniffer()
        delimiter = sniffer.sniff(file_content).delimiter
        
        # Ler o CSV com o delimitador detectado
        return pd.read_csv(file, delimiter=delimiter, low_memory=False)
    elif file_type == "xlsx":
        return pd.read_excel(file, engine="openpyxl")
    return None

# Upload do arquivo CSV ou XLSX
uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV ou XLSX", type=["csv", "xlsx"])

if uploaded_file:
    # Detectar o tipo de arquivo
    file_type = uploaded_file.name.split(".")[-1]  # Detectar o tipo de arquivo (csv ou xlsx)
    
    # Carregar os dados no DataFrame
    df = load_data(uploaded_file, file_type)

    if df is not None:
        # Exibir informações do arquivo
        st.info(f"""
            📊 **Informações do arquivo:**
            - Total de linhas: {len(df)}
            - Total de colunas: {len(df.columns)}
        """)

        st.warning("⚠️ **Atenção**: A tabela abaixo mostra apenas as 5 primeiras linhas do arquivo para referência das colunas disponíveis. O processamento será realizado com o arquivo completo.")
        
        st.write("Pré-visualização (5 primeiras linhas):")
        st.dataframe(df.head())

        # Converter para Parquet
        parquet_buffer = BytesIO()
        table = pa.Table.from_pandas(df)
        pq.write_table(table, parquet_buffer)
        parquet_buffer.seek(0)  # Voltar para o início do buffer após escrever o parquet

        # Carregar o arquivo Parquet para processamento
        df_parquet = pd.read_parquet(parquet_buffer)

        # Escolha das colunas
        st.sidebar.header("Configurações do processamento")
        colunas_disponiveis = df_parquet.columns.tolist()
        
        colunas_selecionadas = st.sidebar.multiselect(
            "Selecione as colunas que deseja manter:",
            options=colunas_disponiveis,
            default=colunas_disponiveis
        )

        coluna_agrupamento = st.sidebar.selectbox(
            "Escolha a coluna para agrupamento:",
            options=colunas_selecionadas
        )

        coluna_operacao = st.sidebar.selectbox(
            "Escolha a coluna para aplicar a operação:",
            options=[col for col in colunas_selecionadas if col != coluna_agrupamento]
        )

        operacao = st.sidebar.radio(
            "Escolha a operação a ser realizada:",
            options=["Soma", "Contagem"]
        )

        # Processar dados com barra de progresso
        if st.sidebar.button("Processar"):
            st.write("Processando os dados...")

            progress_bar = st.progress(0)  # Inicializa a barra de progresso

            # Simulação de etapas de processamento
            total_etapas = 5  # Número de passos
            for etapa in range(total_etapas):
                time.sleep(0.5)  # Simula o tempo de processamento
                progress_bar.progress((etapa + 1) / total_etapas)

            # Realiza o processamento com base na operação escolhida
            if operacao == "Soma":
                resultado = (
                    df_parquet.groupby(coluna_agrupamento)[coluna_operacao]
                    .sum(numeric_only=True)
                    .reset_index()
                )
            elif operacao == "Contagem":
                resultado = (
                    df_parquet.groupby(coluna_agrupamento)[coluna_operacao]
                    .nunique()
                    .reset_index(name="Contagem")
                )

            st.success("Processamento concluído!")
            
            # Mostrar resultado com informações adicionais
            st.write("Resultado do processamento (arquivo completo):")
            st.dataframe(resultado)

            # Baixar o arquivo processado em CSV ou XLSX dependendo do tipo original
            if file_type == "csv":
                csv_resultado = resultado.to_csv(index=False, encoding="utf-8-sig")  # Codificação UTF-8 com BOM
                st.download_button(
                    label="Baixar arquivo processado (CSV)",
                    data=csv_resultado,
                    file_name="resultado.csv",
                    mime="text/csv"
                )
            elif file_type == "xlsx":
                output = BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    resultado.to_excel(writer, index=False, sheet_name="Resultado")
                st.download_button(
                    label="Baixar arquivo processado (XLSX)",
                    data=output.getvalue(),
                    file_name="resultado.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
