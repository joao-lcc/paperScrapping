import streamlit as st
import pandas as pd
from exa_py import Exa
import os
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo key.env
load_dotenv("key.env")

# Obter o token da API
EXA_API_KEY = os.getenv("EXA_API_KEY")
exa = Exa(EXA_API_KEY)

# Dicionário de mapeamento de domínios para revistas e qualis
journal_mapping = {
    "nature.com": ("Nature Medicine", "A1"),
    "nejm.org": ("New England Journal of Medicine", "A1"),
    "lancet.com": ("The Lancet", "A1"),
    "jamanetwork.com": ("JAMA", "A1"),
    "sciencedirect.com": ("Elsevier (ScienceDirect)", "A1"),
    "pubmed.ncbi.nlm.nih.gov": ("PubMed", "A1"),
    "link.springer.com": ("SpringerLink", "A1"),
    "onlinelibrary.wiley.com": ("Wiley Online Library", "A1"),
    "academic.oup.com": ("Oxford Academic", "A1"),
    "tandfonline.com": ("Taylor & Francis", "A1"),
    "bmj.com": ("British Medical Journal (BMJ)", "A1"),
    "cell.com": ("Cell Press", "A1"),
    "plos.org": ("PLOS", "A1"),
    "ieeexplore.ieee.org": ("IEEE Xplore", "A1"),
    "dl.acm.org": ("ACM Digital Library", "A1"),
}

# Identificar a revista com base no domínio
def identificar_journal(url):
    for domain, (journal, qualis) in journal_mapping.items():
        if domain in url:
            return journal, qualis
    return "Desconhecido", "Desconhecido"

# Título do aplicativo
st.title("Pesquisa de Artigos Científicos")

st.write("Olá! Este é um aplicação para pesquisa de artigos científicos em revistas de alto impacto. O mecanismo de busca é alimentado pela Exa API, que permite buscar artigos em diversas fontes de informação. Utilize a caixa de texto abaixo para inserir o tema da sua pesquisa e veja na tabela os artigos encontrados.")

# Caixa de texto para inserir o tema da pesquisa
search_term = st.text_input("Digite o tema da sua pesquisa:")

if search_term:
    # Definir o termo de busca com os sites específicos
    search_query = f"{search_term} site:nature.com OR site:nejm.org OR site:lancet.com OR site:jamanetwork.com OR site:sciencedirect.com OR site:pubmed.ncbi.nlm.nih.gov OR site:link.springer.com OR site:onlinelibrary.wiley.com OR site:academic.oup.com OR site:tandfonline.com OR site:bmj.com OR site:cell.com OR site:plos.org OR site:ieeexplore.ieee.org OR site:dl.acm.org"


    # Fazer a busca na Exa API
    search_response = exa.search_and_contents(
        search_query,
        highlights={"num_sentences": 2},
        num_results=40  # Número de artigos a buscar
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
            year = article.published_date[:4] if article.published_date else "Desconhecido"


            journal, qualis = identificar_journal(url)


            # Adicionar os dados na lista
            data.append([title, year, journal, qualis, url])

        # Criar um DataFrame para organizar os dados
        df_articles = pd.DataFrame(data, columns=["Título", "Ano", "Revista", "Qualis", "URL"])

        # Filtros
        st.sidebar.header("Filtros")

        # Filtro por ano
        anos_disponiveis = df_articles["Ano"].unique()
        ano_selecionado = st.sidebar.selectbox("Selecione o ano", ["Todos"] + sorted(anos_disponiveis, reverse=True))

        # Filtro por revista
        revistas_disponiveis = df_articles["Revista"].unique()
        revistas_selecionadas = st.sidebar.multiselect("Selecione as revistas", revistas_disponiveis, default=revistas_disponiveis)

        # Aplicar filtros
        if ano_selecionado != "Todos":
            df_articles = df_articles[df_articles["Ano"] == ano_selecionado]
            st.session_state.pagina_atual = 1
        df_articles = df_articles[df_articles["Revista"].isin(revistas_selecionadas)]

        # Paginação
        items_por_pagina = 8
        total_paginas = (len(df_articles) // items_por_pagina + (1 if len(df_articles) % items_por_pagina > 0 else 0))

        # Exibir os dados da página atual

        if "pagina_atual" not in st.session_state:
            st.session_state.pagina_atual = 1
        inicio = (st.session_state.pagina_atual - 1) * items_por_pagina
        fim = inicio + items_por_pagina
        df_pagina = df_articles.iloc[inicio:fim]

        st.dataframe(df_pagina)



        # Botões de navegação
        col1, col2, col3 = st.columns([1, 1, 1])
        with col1:
            if st.button("Anterior") and st.session_state.pagina_atual > 1:
                st.session_state.pagina_atual -= 1
        with col2:
            st.write(f"Página {st.session_state.pagina_atual} de {total_paginas}")
        with col3:
            if st.button("Próxima") and st.session_state.pagina_atual < total_paginas:
                st.session_state.pagina_atual += 1



        # Opção para baixar a tabela como CSV
        csv = df_articles.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Baixar tabela como CSV",
            data=csv,
            file_name='artigos.csv',
            mime='text/csv',
        )