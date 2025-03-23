import streamlit as st
import pandas as pd
import re
from exa_py import Exa
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo key.env
load_dotenv("key.env")

# Obter o token da API
EXA_API_KEY = os.getenv("EXA_API_KEY")
exa = Exa(EXA_API_KEY)

# Título do aplicativo
st.title("Pesquisa de Artigos Científicos")

# Caixa de texto para inserir o tema da pesquisa
search_term = st.text_input("Digite o tema da sua pesquisa:")

if search_term:
    # Definir o termo de busca com os sites específicos
    search_query = f"{search_term} site:nature.com OR site:nejm.org OR site:lancet.com OR site:jamanetwork.com OR site:sciencedirect.com"

    # Fazer a busca na Exa API
    search_response = exa.search_and_contents(
        search_query,
        highlights={"num_sentences": 2},
        num_results=10  # Número de artigos a buscar
    )

    # Exibir os resultados encontrados
    articles = search_response.results

    if not articles:
        st.write("Nenhum artigo encontrado.")
    else:
        st.write(f"🔍 {len(articles)} artigos encontrados sobre {search_term}.\n")

        # Lista para armazenar os dados dos artigos
        data = []

        for article in articles:
            # Extrair o título, URL e snippet do artigo
            title = article.title
            url = article.url
            snippet = article.text[:300] if article.text else "Resumo não disponível"

            # Identificar o ano no snippet (supondo que esteja no formato 202X)
            year_match = re.search(r"20\d{2}", snippet)
            year = year_match.group(0) if year_match else "Desconhecido"

            # Identificar a revista com base no domínio do site
            if "nature.com" in url:
                journal = "Nature Medicine"
                qualis = "A1"
            elif "nejm.org" in url:
                journal = "New England Journal of Medicine"
                qualis = "A1"
            elif "lancet.com" in url:
                journal = "The Lancet"
                qualis = "A1"
            elif "jamanetwork.com" in url:
                journal = "JAMA"
                qualis = "A1"
            elif "sciencedirect.com" in url:
                journal = "Elsevier (ScienceDirect)"
                qualis = "A1"
            else:
                journal = "Desconhecido"
                qualis = "Desconhecido"

            # Adicionar os dados na lista
            data.append([title, year, journal, qualis, url])

        # Criar um DataFrame para organizar os dados
        df_articles = pd.DataFrame(data, columns=["Título", "Ano", "Revista", "Qualis", "URL"])

        # Exibir a tabela no Streamlit
        st.dataframe(df_articles)

        # Opção para baixar a tabela como CSV
        csv = df_articles.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar tabela como CSV",
            data=csv,
            file_name='artigos.csv',
            mime='text/csv',
        )