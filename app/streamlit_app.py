# LIBS
import pandas as pd
import streamlit as st
from utils.extracao_dados import extracao_dados, min_max_prices

# CONFIGURACOES STREAMLIT
st.set_page_config(
    page_title = "Preços de Carne El Chañar",
    layout = 'wide',
    menu_items = {
        'about': 'Criado por josenilton1878@gmail.com'
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

# DADOS ATUALIZADOS
st.markdown(
    '## Dados Tabelados do Preço da Carne no Dia Atual'
)

df = (
    extracao_dados()
    .pipe(
        lambda df: df.loc[
            (df.tipo_carne.isin(st.session_state.tipo_carnes))
            & (df.preco_kg.between(preco_min, st.session_state.faixa_precos))
        ]
    )
)

st.dataframe(
    data = df,
    use_container_width = True
)