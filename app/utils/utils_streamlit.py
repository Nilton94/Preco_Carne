# LIBS
import pandas as pd
import streamlit as st
from utils.extracao_dados import extracao_dados, min_max_prices
from utils.utils_numbers import millify
import os, datetime

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

    st.markdown('---')