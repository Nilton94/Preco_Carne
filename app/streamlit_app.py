# LIBS
import pandas as pd
import os
import streamlit as st
from utils.extracao_dados import extracao_dados
from utils.utils_streamlit import get_metrics, get_widgets, get_table, get_calc, get_config

# CONFIGURACOES STREAMLIT
get_config()

# WIDGETS
get_widgets()

# METRICAS
get_metrics()

# DADOS ATUALIZADOS
get_table()

# CALCULADORA
get_calc()

st.write(
    os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze')
)