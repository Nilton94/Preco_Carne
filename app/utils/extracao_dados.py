import pandas as pd
import requests
from bs4 import BeautifulSoup
import re
import datetime
import pytz
import streamlit as st
import pyarrow.parquet as pq
import pyarrow as pa
import os

# Cacheando os dados carregados, com permanência de 5 hs (18000 s) e máximo de 10 entradas
st.cache_data(ttl = 18000, max_entries = 10)
def extracao_dados():
    '''
        ### Objetivo:
        - Extrair dados do preço de carne do site elchañar
    '''
    
    # LISTA DE URLS COM CADA TIPO DE CARNE
    urls = [
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/1/carne-vacuna',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/4/pollo',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/3/cerdo',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/2/otras-carnes',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/6/achuras-y-menudencias',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/11/embutidos',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/9/elaborados',
        'https://www.xn--carneselchaar-skb.com.ar/productos/rubros/10/elaborados-premium'
    ]

    # LISTA PARA GUARDAR OS DADOS
    dados = []

    for url in urls:

        # REQUISICAO
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser').find('div', 'col-md-8')

        for i in soup.find_all('div', 'row'):
        
            # VALORES DE DATA
            data = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S'))
            ano = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).year)
            mes = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).month)
            dia = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).day)

            # TIPO DA CARNE
            try:
                tipo_carne = re.search(r'[^/]+$', url).group(0)
            except:
                tipo_carne = 'Sem info'

            # NOME DA CARNE
            try:
                nome_carne = i.find('h3', 'h4 text-dark').text.strip()
            except:
                nome_carne = 'Sem info'

            # MOEDA
            try:
                moeda = re.sub('[0-9\\.]','', i.find('div', 'col-xs-8 col-sm-2 d-flex align-items-center justify-content-end').find('h3').text)
            except:
                moeda = 'Sem info'

            # PRECO POR KG
            try:
                preco_kg = float(re.sub('[^0-9\\.]','', i.find('div', 'col-xs-8 col-sm-2 d-flex align-items-center justify-content-end').find('h3').text))
            except:
                preco_kg = 0


            dados.append(
                [
                    tipo_carne,
                    nome_carne,
                    moeda,
                    preco_kg,
                    data,
                    ano,
                    mes,
                    dia
                ]
            )

    # DATAFRAME FINAL
    df_carnes = pd.DataFrame(
        dados,
        columns = ['tipo_carne', 'nome_carne', 'moeda', 'preco_kg', 'data', 'ano', 'mes', 'dia']
    )

    # SALVANDO COMO PARQUET
    pq.write_to_dataset(
        table = pa.Table.from_pandas(df_carnes),
        root_path = os.path.join(os.getcwd(), 'app', 'data', 'bronze'),
        partition_cols = ['ano','mes','dia'],
        # partition_filename_cb = lambda x: '-'.join(x)+'.parquet', (Não funciona com o uso o use_legacy_dataset = False, que é necessário para usar o existing_data_behaviour)
        existing_data_behavior = 'delete_matching',
        use_legacy_dataset = False
    )

    return df_carnes

