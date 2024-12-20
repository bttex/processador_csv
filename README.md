# Processador de Arquivos

Um aplicativo web desenvolvido com Streamlit para processar arquivos CSV e XLSX de forma eficiente, permitindo agrupamento e operações de soma e contagem em grandes conjuntos de dados.

## 🚀 Funcionalidades

- Upload de arquivos CSV e XLSX
- Visualização prévia dos dados
- Seleção flexível de colunas
- Operações de agrupamento com soma ou contagem
- Exportação dos resultados em CSV ou XLSX
- Interface amigável com barra de progresso
- Suporte a arquivos grandes (até 5GB)

## 📋 Pré-requisitos

```
streamlit
pandas
```

## 🔧 Instalação

1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

## 🖥️ Como usar

1. Execute o aplicativo:
```bash
streamlit run app.py
```

2. Acesse o aplicativo no navegador (normalmente http://localhost:8501)

3. Siga os passos na interface:
   - Faça upload do arquivo CSV ou XLSX
   - Selecione as colunas desejadas no painel lateral
   - Escolha a coluna para agrupamento
   - Selecione a operação (Soma ou Contagem)
   - Clique em "Processar"
   - Baixe o resultado processado

## 🎯 Características Principais

### Interface Personalizada
- Texto em português
- Mensagens informativas sobre o progresso

### Processamento de Dados
- Suporte a arquivos grandes com `low_memory=False`
- Cache de dados para melhor performance
- Visualização prévia limitada a 5 linhas
- Informações sobre total de linhas e colunas

### Operações Disponíveis
- **Soma**: Agrupa e soma valores numéricos
- **Contagem**: Conta valores únicos em cada grupo

## ⚠️ Limitações

- Tipos de arquivo suportados: apenas CSV e XLSX
- Limite de tamanho por arquivo: 5GB
- A soma só funciona em colunas numéricas

## 🔍 Detalhes Técnicos

### Componentes Principais
- `st.file_uploader`: Gerencia upload de arquivos
- `pd.read_csv/read_excel`: Lê os arquivos
- `st.cache_data`: Otimiza carregamento de dados
- `groupby`: Realiza operações de agrupamento
- `BytesIO`: Gerencia exportação de arquivos

## 📝 Notas de Uso

1. **Performance**
   - Use arquivos CSV para melhor performance
   - Evite selecionar colunas desnecessárias

2. **Memória**
   - O aplicativo carrega o arquivo inteiro na memória
   - Monitore o uso de RAM com arquivos muito grandes

3. **Formatos de Dados**
   - Certifique-se que as colunas numéricas estão no formato correto
   - Verifique a codificação de arquivos CSV

## 🤝 Contribuindo

1. Faça um Fork do projeto
2. Crie sua Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. Push para a Branch (`git push origin feature/AmazingFeature`)
5. Abra um Pull Request

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais informações.
