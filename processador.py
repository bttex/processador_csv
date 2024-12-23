import streamlit as st
import pandas as pd
import time
from io import BytesIO
from io import StringIO
import pyarrow.parquet as pq
import pyarrow as pa
import csv
from charset_normalizer import detect

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
@st.cache_data(show_spinner=False)
def load_data(file, file_type):
    if file_type == "csv":
        # Lista de encodings comuns para tentar
        encodings = ['utf-8', 'latin1', 'iso-8859-1', 'cp1252']
        
        # Lista de delimitadores comuns
        delimiters = [';', ',', '\t', '|']
        
        # Ler o conteúdo do arquivo uma única vez
        file_content = file.read()
        
        # Tentar diferentes encodings
        for encoding in encodings:
            try:
                # Decodificar o conteúdo com o encoding atual
                str_content = file_content.decode(encoding)
                
                # Criar um StringIO object para simular um arquivo
                string_data = StringIO(str_content)
                
                # Tentar detectar o delimitador com o Sniffer usando uma amostra
                sample = str_content[:1024]
                try:
                    dialect = csv.Sniffer().sniff(sample)
                    delimiter = dialect.delimiter
                except:
                    # Se o Sniffer falhar, tentar cada delimitador
                    for delimiter in delimiters:
                        try:
                            # Criar novo StringIO para cada tentativa
                            string_data = StringIO(str_content)
                             # Ler o CSV forçando todas as colunas como string primeiro
                            df = pd.read_csv(
                                string_data,
                                delimiter=delimiter,
                                low_memory=True,
                                on_bad_lines='skip',
                                dtype=str  # Força todas as colunas como string
                            )
                             # Verificar se o DataFrame foi criado corretamente
                            if len(df.columns) > 1:
                                # Tentar converter colunas numéricas de forma segura
                                for col in df.columns:
                                    try:
                                        # Tenta converter para numérico, ignorando erros
                                        numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                                        # Se mais de 70% dos valores são números válidos, converte a coluna
                                        if numeric_conversion.notna().mean() > 0.7:
                                            df[col] = numeric_conversion
                                    except:
                                        continue
                                
                                return df
                        except Exception as e:
                            continue
                else:
                    # Se o Sniffer funcionou, tentar ler com o delimitador detectado
                    try:
                        df = pd.read_csv(
                            StringIO(str_content),
                            delimiter=delimiter,
                            low_memory=True,
                            on_bad_lines='skip',
                            dtype=str  # Força todas as colunas como string
                        )
                        
                        if len(df.columns) > 1:
                            # Tentar converter colunas numéricas de forma segura
                            for col in df.columns:
                                try:
                                    numeric_conversion = pd.to_numeric(df[col], errors='coerce')
                                    if numeric_conversion.notna().mean() > 0.7:
                                        df[col] = numeric_conversion
                                except:
                                    continue
                            
                            return df
                    except:
                        continue
            
            except UnicodeDecodeError:
                continue
                
        # Se nenhuma combinação funcionou
        st.error("Não foi possível ler o arquivo CSV. Tente verificar o encoding e o delimitador do arquivo.")
        return None
            
    elif file_type == "xlsx":
        try:
            return pd.read_excel(file, engine="openpyxl")
        except Exception as e:
            st.error(f"Erro ao processar o arquivo Excel: {e}")
            return None
            
    return None


@st.cache_data(show_spinner=False)
def convert_to_parquet(df):
    parquet_buffer = BytesIO()
    table = pa.Table.from_pandas(df)
    pq.write_table(table, parquet_buffer)
    parquet_buffer.seek(0)
    return parquet_buffer

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

# Upload do arquivo CSV ou XLSX
uploaded_file = st.file_uploader("Faça o upload de um arquivo CSV ou XLSX", type=["csv", "xlsx"])

if uploaded_file is not None:
    # Só carregar se ainda não tivermos dados ou se for um arquivo diferente
    file_hash = hash(uploaded_file.read())
    uploaded_file.seek(0)
    
    if st.session_state.df is None or st.session_state.current_file_hash != file_hash:
        with st.spinner("Lendo o arquivo, por favor aguarde..."):
            file_type = uploaded_file.name.split(".")[-1]
            df = load_data(uploaded_file, file_type)
            
            if df is not None:
                # Converter para Parquet
                parquet_buffer = convert_to_parquet(df)
                df_parquet = pd.read_parquet(parquet_buffer)
                
                # Armazenar no session_state
                st.session_state.df = df
                st.session_state.df_parquet = df_parquet
                st.session_state.file_type = file_type
                st.session_state.current_file_hash = file_hash

                # Exibir mensagem de sucesso apenas no primeiro carregamento
                success_message = st.success("Arquivo carregado com sucesso!")
                time.sleep(3)
                success_message.empty()

    # Se temos dados carregados
    if st.session_state.df is not None:
        df = st.session_state.df
        df_parquet = st.session_state.df_parquet
        
        st.info(f"""
            📊 **Informações do arquivo:**
            - Total de linhas: {len(df)}
            - Total de colunas: {len(df.columns)}
        """)

        st.warning("⚠️ **Atenção**: A tabela abaixo mostra apenas as 5 primeiras linhas do arquivo para referência das colunas disponíveis. O processamento será realizado com o arquivo completo.")
        
        st.write("Pré-visualização (5 primeiras linhas):")
        st.dataframe(df.head())

        # Sidebar com configurações
        st.sidebar.header("Configurações do processamento")
        colunas_disponiveis = df_parquet.columns.tolist()
        
        colunas_selecionadas = st.sidebar.multiselect(
            "Selecione as colunas que deseja manter:",
            options=colunas_disponiveis,
            default=colunas_disponiveis
        )

        # Filtro por Intervalo de Datas (opcional)
        coluna_data = st.sidebar.selectbox("Selecione a coluna de data para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
        if coluna_data != "Nenhuma":
            data_inicio = st.sidebar.date_input("Data de início", value=pd.to_datetime(df_parquet[coluna_data]).min())
            data_fim = st.sidebar.date_input("Data de fim", value=pd.to_datetime(df_parquet[coluna_data]).max())

        # Filtro por Valor Numérico (opcional)
        coluna_valor = st.sidebar.selectbox("Selecione a coluna numérica para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
        if coluna_valor != "Nenhuma":
            valor_min = st.sidebar.number_input("Valor mínimo", value=float(df_parquet[coluna_valor].min()))
            valor_max = st.sidebar.number_input("Valor máximo", value=float(df_parquet[coluna_valor].max()))

        # Filtro por Texto (opcional)
        coluna_texto = st.sidebar.selectbox("Selecione a coluna de texto para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
        if coluna_texto != "Nenhuma":
            texto_filtro = st.sidebar.text_input("Texto para filtrar")

        # Filtro por Categoria (opcional)
        coluna_categoria = st.sidebar.selectbox("Selecione a coluna de categoria para filtrar (opcional):", options=["Nenhuma"] + colunas_disponiveis)
        if coluna_categoria != "Nenhuma":
            categorias_selecionadas = st.sidebar.multiselect("Selecione as categorias:", options=df_parquet[coluna_categoria].unique())

        if colunas_selecionadas:
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

            # Processar dados
            if st.sidebar.button("Processar"):
                st.write("Processando os dados...")
                progress_bar = st.progress(0)

                # Aplicar filtros
                df_filtrado = df_parquet.copy()
                if coluna_data != "Nenhuma":
                    df_filtrado = df_filtrado[(pd.to_datetime(df_filtrado[coluna_data]) >= data_inicio) & (pd.to_datetime(df_filtrado[coluna_data]) <= data_fim)]
                if coluna_valor != "Nenhuma":
                    df_filtrado = df_filtrado[(df_filtrado[coluna_valor] >= valor_min) & (df_filtrado[coluna_valor] <= valor_max)]
                if coluna_texto != "Nenhuma":
                    df_filtrado = df_filtrado[df_filtrado[coluna_texto].str.contains(texto_filtro, na=False)]
                if coluna_categoria != "Nenhuma":
                    df_filtrado = df_filtrado[df_filtrado[coluna_categoria].isin(categorias_selecionadas)]

                # Simulação de progresso
                total_etapas = 5
                for etapa in range(total_etapas):
                    time.sleep(0.5)
                    progress_bar.progress((etapa + 1) / total_etapas)

                # Realizar processamento usando o DataFrame filtrado
                if operacao == "Soma":
                    resultado = (
                        df_filtrado[colunas_selecionadas].groupby(coluna_agrupamento)[coluna_operacao]
                        .sum(numeric_only=True)
                        .reset_index()
                    )
                else:  # Contagem
                    resultado = (
                        df_filtrado[colunas_selecionadas].groupby(coluna_agrupamento)[coluna_operacao]
                        .nunique()
                        .reset_index(name="Contagem")
                    )

                st.session_state.processed_result = resultado
                st.success("Processamento concluído!")

                # Mostrar resultado
                st.write("Resultado do processamento (arquivo completo):")
                st.dataframe(resultado)

                # Botões de download
                if st.session_state.file_type == "csv":
                    csv_resultado = resultado.to_csv(index=False, encoding="utf-8-sig")
                    st.download_button(
                        label="Baixar arquivo processado (CSV)",
                        data=csv_resultado,
                        file_name="resultado.csv",
                        mime="text/csv"
                    )
                else:  # xlsx
                    output = BytesIO()
                    with pd.ExcelWriter(output, engine="openpyxl") as writer:
                        resultado.to_excel(writer, index=False, sheet_name="Resultado")
                    st.download_button(
                        label="Baixar arquivo processado (XLSX)",
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
        st.session_state.df = None
        st.session_state.df_parquet = None
        st.session_state.processed_result = None
        st.session_state.file_type = None
        st.session_state.current_file_hash = None
        
        # Exibe a mensagem de sucesso
        success_message = st.success("Arquivo removido com sucesso.")
        
        # Aguarda alguns segundos e limpa a mensagem
        time.sleep(3)
        success_message.empty()
