# LIBS
import pandas as pd
import streamlit as st
from bs4 import BeautifulSoup
from utils.extracao_dados import extracao_dados, min_max_prices

# CONFIGURACOES STREAMLIT
st.set_page_config(
    page_title = "Preços de Carne El Chañar",
    layout = 'wide',
    menu_items = {
        'about': 'App simples para obter preço mais recente das carnes do El Chañar. Criado por josenilton1878@gmail.com'
    }

)
# WIDGETS
st.sidebar.multiselect(
    'Tipos de Carne',
    options = ['carne-vacuna', 'pollo', 'cerdo', 'otras-carnes', 'achuras-y-menudencias', 'embutidos', 'elaborados', 'elaborados-premium'],
    key = 'tipo_carnes'
)

preco_min, preco_max = min_max_prices()
st.sidebar.slider(
    'Faixa de preços (Kg)',
    min_value = preco_min,
    max_value = preco_max,
    key = 'faixa_precos'
)

st.sidebar.button(
    label = 'Atualizar dados',
    key = 'atualizar'
)

# DADOS ATUALIZADOS
st.markdown(
    '## Dados Tabelados do Preço da Carne no Dia Atual'
)

if st.session_state.atualizar:
    # BASE
    df = (
        extracao_dados()
        .pipe(
            lambda df: df.loc[
                (df.tipo_carne.isin(st.session_state.tipo_carnes))
                & (df.preco_kg.between(preco_min, st.session_state.faixa_precos))
            ]
        )
        [['tipo_carne','nome_carne', 'moeda', 'preco_kg', 'data']]
    )

    # AGG
    df_vacuna = df.loc[df.tipo_carne == 'carne-vacuna', 'preco_kg'].median()
    df_pollo = df.loc[df.tipo_carne == 'pollo', 'preco_kg'].median()
    df_cerdo = df.loc[df.tipo_carne == 'cerdo', 'preco_kg'].median()

    # CARDS
    # col1, col2, col3 = st.columns(3)

    # col1.markdown(f'#### Mediana Vacuna: {df_vacuna}')
    # col2.markdown(f'#### Mediana Pollo: {df_pollo}')
    # col3.markdown(f'#### Mediana Cerdo: {df_cerdo}')

    st.dataframe(
        data = df,
        use_container_width = True,
        hide_index = True
    )


# CALCULADORA
# st.markdown(
#     '## Calculadora'
# )