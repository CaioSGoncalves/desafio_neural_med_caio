# Use a imagem base oficial do Python
FROM python:3.11-slim

# Defina o diretório de trabalho dentro do container
WORKDIR /app

# Copie o arquivo de dependências (será criado posteriormente)
COPY requirements.txt .

# Instale as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Copie o código do serviço para o container
COPY . .


# Expondo a porta onde o Streamlit vai rodar
EXPOSE 8501

# Comando para rodar a aplicação Streamlit
CMD ["streamlit", "run", "front.py"]
