# LIBS
import pandas as pd
import streamlit as st
from utils.extracao_dados import extracao_dados
from utils.utils_streamlit import get_metrics, get_widgets

# CONFIGURACOES STREAMLIT
st.set_page_config(
    page_title = "Preços de Carne El Chañar",
    layout = 'wide',
    menu_items = {
        'about': 'App simples para obter preço mais recente das carnes do El Chañar. Criado por josenilton1878@gmail.com'
    }

)
# WIDGETS
get_widgets()

# METRICAS
get_metrics()

# DADOS ATUALIZADOS
if 'tabelados' not in st.session_state:
    st.session_state['tabelados'] = []

with st.expander('**Dados Tabelados do Preço da Carne no Dia Atual**'):

    if st.session_state.atualizar or len(st.session_state['tabelados']) > 0:
        # BASE
        df = (
            extracao_dados()
            .pipe(
                lambda df: df.loc[
                    (df.tipo_carne.isin(st.session_state.tipo_carnes))
                    & (df.preco_kg.between(st.session_state.faixa_precos[0], st.session_state.faixa_precos[1]))
                ]
            )
            [['tipo_carne','nome_carne', 'moeda', 'preco_kg', 'data']]
        )
        st.session_state['tabelados'].append(df.to_dict(orient='list'))

        # # AGG
        # df_vacuna = df.loc[df.tipo_carne == 'carne-vacuna', 'preco_kg'].median()
        # df_pollo = df.loc[df.tipo_carne == 'pollo', 'preco_kg'].median()
        # df_cerdo = df.loc[df.tipo_carne == 'cerdo', 'preco_kg'].median()

        # # CARDS
        # col1, col2, col3 = st.columns(3)

        # col1.metric('Mediana Vacuna', value = df_vacuna)
        # col2.metric('Mediana Pollo', value = df_pollo)
        # col3.metric('Mediana Cerdo', value = df_cerdo)

        st.dataframe(
            data = st.session_state['tabelados'][-1],
            use_container_width = True,
            hide_index = True
        )
    else:
        st.write(':red[Selecione ao menos um tipo de carne!]')

# CALCULADORA
if 'items' not in st.session_state:
    st.session_state['items'] = []

with st.expander('**Calculadora**'):

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