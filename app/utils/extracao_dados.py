import pandas as pd
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
import re
import datetime
import pytz
import streamlit as st
import pyarrow.parquet as pq
import pyarrow as pa
import os

# Cacheando os dados carregados, com permanência de 5 hs (18000 s) e máximo de 10 entradas

def get_cambio():

    try:
        r = requests.get('https://wise.com/es/currency-converter/brl-to-ars-rate', headers={'user-agent':UserAgent().get_random_user_agent(), 'encoding': 'utf-8'})
        tag = BeautifulSoup(r.text, 'html.parser').find('h3', 'cc__source-to-target').text

        currency = re.findall(r'([\d,.]+)\s*([A-Za-z$]+)', tag)
        final = {f'{currency[0][1]}->{currency[1][1]}': float(currency[1][0].replace(',', '.'))}

        return final
    except Exception as e:
        return {'R$->$': 0.0}

@st.cache_data(ttl = 18000, max_entries = 10)
def get_urls():
    try:
        r = requests.get('https://carneselchaniar.com.ar/shop', headers={'user-agent':UserAgent().get_random_user_agent()})

        urls = [i.find('a')['href'] for i in BeautifulSoup(r.text, 'html.parser').find('div', {'class':"row rubros products-big"}) if i != '\n']

        final_urls = {
            re.findall(r'https://carneselchaniar.com.ar/shop/rubros/[0-9]{1,2}/[0-9]{1,2}-(\w.*)', url)[0]: url 
            for url in urls
        }

        return final_urls
    except Exception as e:
        return f'Erro: {e}'


@st.cache_data(ttl = 18000, max_entries = 10)
def extracao_dados():
    '''
        ### Objetivo:
        - Extrair dados do preço de carne do site elchañar
    '''
    
    cambio = get_cambio()['R$->$']*1.13
    
    urls_dict = get_urls()
    urls = list(urls_dict.values())
    tipos = list(urls_dict.keys())

    # LISTA PARA GUARDAR OS DADOS
    dados = []

    for tipo, url in urls_dict.items():

        # REQUISICAO
        response = requests.get(url, headers={'user-agent':UserAgent().get_random_user_agent()})

        produtos = BeautifulSoup(response.text, 'html.parser').find_all("div", class_=lambda c: c and "hidden sinmarca" in c)
        # nomes = [i.find('a', class_ = lambda c: c and 'text-decoration-none' in c).text for i in produtos]
        # precos = [(i.find('h3').text).strip() for i in produtos if i.find('h3') is not None]

        for i in produtos:
        
            # VALORES DE DATA
            data = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).strftime('%Y-%m-%d %H:%M:%S'))
            ano = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).year)
            mes = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).month)
            dia = str(datetime.datetime.now(tz = pytz.timezone('America/Sao_Paulo')).replace(microsecond=0).day)

            # TIPO DA CARNE
            try:
                tipo_carne = tipo
            except:
                tipo_carne = 'Sem info'

            # NOME DA CARNE
            try:
                nome_carne = i.find('a', class_ = lambda c: c and 'text-decoration-none' in c).text
            except:
                nome_carne = 'Sem info'

            # MOEDA
            try:
                moeda = re.search(r'\$|R\$', i.find('h3').text).group(0)
            except:
                moeda = 'Sem info'

            # PRECO POR KG
            try:
                preco_kg = float(re.sub(r'\.|\$', '', i.find('h3').text).replace(',', '.'))
            except:
                preco_kg = 0


            dados.append(
                [
                    tipo_carne,
                    nome_carne,
                    moeda,
                    preco_kg,
                    cambio,
                    data,
                    ano,
                    mes,
                    dia
                ]
            )

    # DATAFRAME FINAL
    df_carnes = pd.DataFrame(
        dados,
        columns = ['tipo_carne', 'nome_carne', 'moeda', 'preco_kg', 'cambio_ars_brl', 'data', 'ano', 'mes', 'dia']
    )

    # SALVANDO COMO PARQUET
    try:
        pq.write_to_dataset(
            table = pa.Table.from_pandas(df_carnes),
            root_path = os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze'),
            partition_cols = ['ano','mes'],
            # partition_filename_cb = lambda x: '-'.join(x)+'.parquet', (Não funciona com o uso o use_legacy_dataset = False, que é necessário para usar o existing_data_behaviour)
            existing_data_behavior = 'error',
            use_legacy_dataset = False
        )
    except:
        pass

    return df_carnes

def min_max_prices():
    
    # Obtendo os preços máximos e mínimos do dia atual
    try:
        df = extracao_dados()
        preco_min, preco_max = df.preco_kg.min(), df.preco_kg.max()
        return preco_min, preco_max
    except:
        return None, None