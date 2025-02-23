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
def extract_data_soychu():
    
    r = requests.get(
        'https://www.pollo27.com.ar/precios/', 
        headers={'user-agent':UserAgent().get_random_user_agent(), 'encoding': 'utf-8'}
    )

    cambio = get_cambio()['R$->$']*1.13
    
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
        - Extrair dados do preço de carne do site elchañar e concatenar com dados do site soychu
    '''
    
    cambio = get_cambio()['R$->$']*1.13
    
    urls_dict = get_urls()
    # urls = list(urls_dict.values())
    # tipos = list(urls_dict.keys())

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

            # MARCA CARNE
            marca_carne = 'EL CHAÑAR'

            # MOEDA
            try:
                moeda = re.search(r'\$|R\$', i.find('h3').text).group(0)
            except:
                moeda = 'Sem info'

            # VALOR ORIGINAL
            try:
                valor_original = float(re.sub(r'\.|\$', '', i.find('h3').text).replace(',', '.'))
            except:
                valor_original = 0

            # QUANTIDADE
            try:
                quantidade = int(re.sub('[^0-9]', '', i.find('a', class_ = lambda c: c and 'text-decoration-none' in c).text)) if 'kilogramo' not in i.find('span').text.lower() else 1
            except:
                quantidade = 1

            # VALOR UNITARIO
            try:
                valor_unitario = valor_original/quantidade
            except:
                valor_unitario = 0

            dados.append(
                [
                    tipo_carne,
                    nome_carne,
                    marca_carne,
                    moeda,
                    valor_original,
                    quantidade,
                    valor_unitario,
                    cambio,
                    data,
                    ano,
                    mes,
                    dia
                ]
            )

    # DATAFRAME EL CHAÑAR
    df_elchanar = pd.DataFrame(
        dados,
        columns = [
            'tipo_carne',
            'nome_carne',
            'marca_carne',
            'moeda',
            'valor_original',
            'quantidade',
            'valor_unitario',
            'cambio_ars_brl',
            'data',
            'ano',
            'mes',
            'dia'
        ]
    )

    # DATAFRAME SOYCHU
    df_soychu = extract_data_soychu()

    # DATAFRAME FINAL
    columns = list(set(df_elchanar.columns).intersection(set(df_soychu.columns)))

    df_final = pd.concat(
        [df_elchanar[columns], df_soychu[columns]], ignore_index=True
    )

    df_final[df_final.select_dtypes(include='float').columns] = df_final.select_dtypes(include='float').round(2)

    df_final = df_final[[
        'marca_carne',
        'tipo_carne',
        'nome_carne',
        'moeda',
        'cambio_ars_brl',
        'valor_original',
        'quantidade',
        'valor_unitario',
        'dia',
        'mes',
        'ano',
        'data'			
    ]]

    # SALVANDO COMO PARQUET
    try:
        pq.write_to_dataset(
            table = pa.Table.from_pandas(df_final),
            root_path = os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze'),
            partition_cols = ['ano','mes'],
            # partition_filename_cb = lambda x: '-'.join(x)+'.parquet', (Não funciona com o uso o use_legacy_dataset = False, que é necessário para usar o existing_data_behaviour)
            existing_data_behavior = 'delete_matching',
            use_legacy_dataset = False
        )
    except:
        pass

    return df_final

def min_max_prices():
    
    # Obtendo os preços máximos e mínimos do dia atual
    try:
        df = extracao_dados()
        preco_min, preco_max = df.valor_original.min(), df.valor_original.max()
        return preco_min, preco_max
    except:
        return None, None