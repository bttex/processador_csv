# Use uma imagem base oficial do Python
FROM python:3.12-slim

# Define o diretório de trabalho dentro do contêiner
WORKDIR /app

# Copia os arquivos de dependências para o contêiner
COPY requirements.txt ./

# Instala as dependências do projeto
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código-fonte para o contêiner
COPY . .

# Expõe a porta usada pelo Streamlit
EXPOSE 8501

# Define o comando para iniciar a aplicação
CMD ["streamlit", "run", "processador.py", "--server.port=8501", "--server.address=0.0.0.0"]
