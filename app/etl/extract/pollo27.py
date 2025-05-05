import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
import re
import datetime
import pytz
import streamlit as st
from utils.cambio import get_cambio

# Cache dos dados carregados, com permanência de 5 hs (18000 s) e máximo de 10 entradas
@st.cache_data(ttl = 18000, max_entries = 10)    
def extract_data_soychu():
    """Retorna os dados de preços de carne do site Pollo 27.

    Returns:
        pandas.Dataframe: Dataframe com os dados de preços de carne do site Pollo 27.
    """

    r = requests.get(
        'https://www.pollo27.com.ar/precios/', 
        headers={
            'user-agent':UserAgent().get_random_user_agent(), 
            'encoding': 'utf-8'
        }
    )

    cambio = get_cambio()['R$->$']
    
    try:
        table = BeautifulSoup(r.text, 'html.parser').find("table").find_all('tr')

        data = [
            {
                'codigo': i.find_all('td')[0].text,
                'nome_carne': i.find_all('td')[1].text,
                'marca_carne': i.find_all('td')[2].text,
                'tipo_carne': i.find_all('td')[3].text,
                # 'valor_original': i.find_all('td')[4].text,
                'moeda': re.search(r'\$|R\$', i.find_all('td')[4].text).group(0),
                'valor_original': float(
                    re.sub(
                        r'\.|\$', 
                        '', 
                        i.find_all('td')[4].text
                    ).replace(',', '.')
                ),
                'quantidade': int(
                    re.sub(
                        '[^0-9]',
                        '',
                        ''.join(re.findall(r'\d{1,}\s{0,1}KG', i.find_all('td')[1].text))
                    )
                    if re.findall(r'\d{1,}\s{0,1}KG', i.find_all('td')[1].text) != []
                    else 1
                ),
                'cambio_ars_brl': cambio,
                'data': str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S')),
                'ano': str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).year),
                'mes': str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).month),
                'dia': str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).day)
            }

            for i in table 
            if i.find_all('td') != []
        ]
    except Exception as e:
        print(f'Erro: {e}')
        data = []

    df = (
        pd.DataFrame(data)
        .assign(
            valor_unitario = lambda x: x['valor_original']/x['quantidade']
        )
    )   

    return df