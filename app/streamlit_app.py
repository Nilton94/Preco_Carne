# LIBS
import pandas as pd
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