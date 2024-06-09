# LIBS
import pandas as pd
import streamlit as st
from utils.extracao_dados import extracao_dados, min_max_prices
from utils.utils_numbers import millify
import os, datetime

def get_config():
    st.set_page_config(
        page_title = "Preços de Carne El Chañar",
        layout = 'wide',
        menu_items = {
            'about': 'App simples para obter preço mais recente das carnes do El Chañar. Criado por josenilton1878@gmail.com'
        }

    )
    
def get_widgets():
    
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
        value = (preco_min, preco_max),
        key = 'faixa_precos'
    )

    st.sidebar.button(
        label = 'Atualizar dados',
        key = 'atualizar'
    ) 

def get_metrics():
    
    # METRICAS
    with st.expander('**Métricas MoM**'):
        df = extracao_dados()
        df_last_month = pd.read_parquet(
            path = os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze'),
            filters = [
                ('ano', '=', (datetime.datetime.now().replace(day = 1).date() - datetime.timedelta(days=1)).year),
                ('mes', '=', (datetime.datetime.now().replace(day = 1).date() - datetime.timedelta(days=0)).month) # AJUSTAR
            ]
        )
        col1, col2, col3 = st.columns(3)

        with col1:
            with st.container(border = True):
                st.markdown('<p style="font-size:35px; text-align:center;"><b>Vacuna</b></p>', unsafe_allow_html=True)
                v1, v2, v3, v4 = st.columns(4, gap='small')

                v1.metric(
                    label = 'Tipos de carne',
                    value = df.loc[df['tipo_carne'] == 'carne-vacuna', 'nome_carne'].count(),
                    delta = float(df.loc[df['tipo_carne'] == 'carne-vacuna', 'nome_carne'].count() - df_last_month.loc[df_last_month['tipo_carne'] == 'carne-vacuna', 'nome_carne'].count()),
                    delta_color = 'normal'
                )

                v2.metric(
                    label = 'Valor Médio ($)',
                    value = millify(round(df.loc[df['tipo_carne'] == 'carne-vacuna', 'preco_kg'].mean(), 2), precision=2),
                    delta = millify((round(df.loc[df['tipo_carne'] == 'carne-vacuna', 'preco_kg'].mean(), 2) - round(df_last_month.loc[df_last_month['tipo_carne'] == 'carne-vacuna', 'preco_kg'].mean(), 2)),precision = 3),
                    delta_color = 'inverse'
                )

                v3.metric(
                    label = 'Preço Mínimo ($)',
                    value = millify(
                        (
                            df
                            .loc[df['tipo_carne'] == 'carne-vacuna', :]
                            .sort_values('preco_kg', ascending = True)
                            .reset_index(drop = True)
                            .to_dict(orient='records')
                            [0]['preco_kg']
                        ), 
                        precision=2
                    ),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )

                v4.metric(
                    label = 'Preço Máximo ($)',
                    value = millify(
                        (
                            df
                            .loc[df['tipo_carne'] == 'carne-vacuna', :]
                            .sort_values('preco_kg', ascending = False)
                            .reset_index(drop = True)
                            .to_dict(orient='records')
                            [0]['preco_kg']
                        ), 
                        precision=2
                    ),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'carne-vacuna', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'carne-vacuna', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )

        with col2:
            with st.container(border = True):
                st.markdown('<p style="font-size:35px; text-align:center;"><b>Pollo</b></p>', unsafe_allow_html=True)
                p1, p2, p3, p4 = st.columns(4)

                p1.metric(
                    label = 'Tipos de carne',
                    value = df.loc[df['tipo_carne'] == 'pollo', 'nome_carne'].count(),
                    delta = float(df.loc[df['tipo_carne'] == 'pollo', 'nome_carne'].count() - df_last_month.loc[df_last_month['tipo_carne'] == 'pollo', 'nome_carne'].count()),
                    delta_color = 'normal'
                )

                p2.metric(
                    label = 'Valor Médio ($)',
                    value = millify(round(df.loc[df['tipo_carne'] == 'pollo', 'preco_kg'].mean(), 2), precision=2),
                    delta = float(round(df.loc[df['tipo_carne'] == 'pollo', 'preco_kg'].mean(), 2) - round(df_last_month.loc[df_last_month['tipo_carne'] == 'pollo', 'preco_kg'].mean(), 2)),
                    delta_color = 'inverse'
                )

                p3.metric(
                    label = 'Preço Mínimo ($)',
                    value = millify(
                        (
                            df
                            .loc[df['tipo_carne'] == 'pollo', :]
                            .sort_values('preco_kg', ascending = True)
                            .reset_index(drop = True)
                            .to_dict(orient='records')
                            [0]['preco_kg']
                        ),
                        precision=2
                    ),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'pollo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'pollo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )

                p4.metric(
                    label = 'Preço Máximo ($)',
                    value = millify((
                        df
                        .loc[df['tipo_carne'] == 'pollo', :]
                        .sort_values('preco_kg', ascending = False)
                        .reset_index(drop = True)
                        .to_dict(orient='records')
                        [0]['preco_kg']
                    ),precision=2),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )

        with col3:
            with st.container(border = True):
                st.markdown('<p style="font-size:35px; text-align:center;"><b>Cerdo</b></p>', unsafe_allow_html=True)
                c1, c2, c3, c4 = st.columns(4)

                c1.metric(
                    label = 'Tipos de carne',
                    value = df.loc[df['tipo_carne'] == 'cerdo', 'nome_carne'].count(),
                    delta = float(df.loc[df['tipo_carne'] == 'cerdo', 'nome_carne'].count() - df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', 'nome_carne'].count()),
                    delta_color = 'normal'
                )

                c2.metric(
                    label = 'Valor Médio ($)',
                    value = millify(round(df.loc[df['tipo_carne'] == 'cerdo', 'preco_kg'].mean(), 2), precision=2),
                    delta = float(round(df.loc[df['tipo_carne'] == 'cerdo', 'preco_kg'].mean(), 2) - round(df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', 'preco_kg'].mean(), 2)),
                    delta_color = 'inverse'
                )

                c3.metric(
                    label = 'Preço Mínimo ($)',
                    value = millify(
                        (
                            df
                            .loc[df['tipo_carne'] == 'cerdo', :]
                            .sort_values('preco_kg', ascending = True)
                            .reset_index(drop = True)
                            .to_dict(orient='records')
                            [0]['preco_kg']
                        ),
                        precision=2
                    ),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = True).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )
                
                c4.metric(
                    label = 'Preço Máximo ($)',
                    value = millify(
                        (
                            df
                            .loc[df['tipo_carne'] == 'cerdo', :]
                            .sort_values('preco_kg', ascending = False)
                            .reset_index(drop = True)
                            .to_dict(orient='records')
                            [0]['preco_kg']
                        ),
                        precision=2
                    ),
                    delta = millify(
                        (
                            df.loc[df['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                            - df_last_month.loc[df_last_month['tipo_carne'] == 'cerdo', :].sort_values('preco_kg', ascending = False).reset_index(drop = True).to_dict(orient='records')[0]['preco_kg']
                        ),
                        precision=3
                    ),
                    delta_color = 'inverse'
                )

        # st.markdown('---')
def get_table():
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

def get_calc():
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