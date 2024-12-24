# Processador de Arquivos

Um aplicativo web desenvolvido com Streamlit para processar arquivos CSV e XLSX de forma eficiente, permitindo agrupamento e operações de soma e contagem em grandes conjuntos de dados.

## 🚀 Funcionalidades

- Upload de arquivos CSV e XLSX
- Visualização prévia dos dados
- Seleção flexível de colunas
- Filtros avançados (opcionais):
  - Filtro por intervalo de datas
  - Filtro por valor numérico
  - Filtro por texto
  - Filtro por categoria
- Operações de agrupamento com soma ou contagem
- Exportação dos resultados em CSV ou XLSX
- Interface amigável com barra de progresso
- Suporte a arquivos grandes (até 5GB)

## 📋 Pré-requisitos

```
streamlit
pandas
pyarrow
openpyxl
charset_normalizer
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
streamlit run processador.py
```

2. Faça o upload de um arquivo CSV ou XLSX
3. Configure os filtros e selecione as colunas desejadas
4. Clique em "Processar" para aplicar os filtros e operações
5. Baixe o arquivo processado em CSV ou XLSX

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
