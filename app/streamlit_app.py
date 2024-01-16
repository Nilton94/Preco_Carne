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

    # USAR st.metric

    st.dataframe(
        data = df,
        use_container_width = True,
        hide_index = True
    )


if 'items' not in st.session_state:
    st.session_state['items'] = []

with st.expander('Calculadora'):

    # WIDGETS
    colu1, colu2, colu3 = st.columns([2,2,2])
    colu1.button(
        label = 'Incluir item na lista',
        key = 'incluir_lista',
        use_container_width = True
    )
    colu2.button(
        label = 'Limpar lista',
        key = 'limpar_lista',
        use_container_width = True
    )
    colu3.button(
        label = 'Calcular valor',
        key = 'calcular_valor',
        type = "primary",
        use_container_width = True
    )

    st.selectbox(
            label = 'Escolha o tipo de carne',
            options = extracao_dados().nome_carne.sort_values().unique(),
            key = 'selecionar_carne'
    )
    st.text_input(
        label = 'Escolha a Quantidade (Kg)',
        key = 'escolher_qtd'
    )

    # DADOS DE INPUT
    if st.session_state.incluir_lista == True:
        st.session_state['items'].append([
            st.session_state.selecionar_carne, 
            float(st.session_state.escolher_qtd.replace(',','.'))
        ])

    # DATAFRAME
    st.markdown('Lista de items')
    lista_df = (
        pd.DataFrame(st.session_state['items'], columns = ['Nome','Quantidade (Kg)'])
        .pipe(
            lambda df: pd.merge(
                left = df, 
                right = extracao_dados(), 
                left_on = 'Nome',
                right_on = 'nome_carne'
            )
        )
        .assign(Total = lambda df: df['Quantidade (Kg)'] * df.preco_kg)
        .rename(columns = {'preco_kg':'Preço por Kg'})
        [['Nome', 'Quantidade (Kg)', 'Preço por Kg', 'Total']]
    )
    st.dataframe(lista_df, hide_index = True)

    # LIMPAR LISTA
    if st.session_state.limpar_lista == True:
        st.session_state['items'] = []

    # CALCULAR VALOR
    if st.session_state.calcular_valor == True:
        valor_total = lista_df['Total'].sum().round(2)
        st.markdown(f'Valor total a ser pago: \n$ {valor_total}')