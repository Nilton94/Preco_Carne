# LIBS
import pandas as pd
import streamlit as st
from utils.extracao_dados import extracao_dados

# CONFIGURACOES STREAMLIT
st.set_page_config(
    page_title = "Preços de Carne El Chañar",
    layout = 'wide',
    menu_items = {
        'about': 'Criado por josenilton1878@gmail.com'
    }

)

# DADOS ATUALIZADOS
st.markdown(
    '## Dados Tabelados do Preço da Carne no Dia Atual'
)
st.dataframe(
    data = extracao_dados(),
    use_container_width = True
)