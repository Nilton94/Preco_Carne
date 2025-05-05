import pandas as pd
import numpy as np
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
import re
import datetime
import pytz
import streamlit as st
import pyarrow.parquet as pq
import pyarrow as pa
import os, logfire
from .logger import get_logger
from .cambio import get_cambio

# Configs
logger = get_logger(level='debug')


# Decorator para criar spans personalizadas no logfire
@logfire.instrument('Extraindo dados do Pollo 27!', record_return=True)
# Cacheando os dados carregados, com permanência de 5 hs e máximo de 10 entradas
@st.cache_data(ttl = datetime.timedelta(hours=5), max_entries = 10, show_spinner = "Extraindo dados do site Pollo 27...")    
def extract_data_soychu():
    
    cambio = get_cambio()['R$->$']
    logger.info('Pollo 27 - Iniciando a coleta de dados do site.')
    
    r = requests.get(
        'https://www.pollo27.com.ar/precios/', 
        headers={'user-agent':UserAgent().get_random_user_agent(), 'encoding': 'utf-8'}
    )
    
    logger.info(f'Pollo 27 - Requests retornaram o código {r.status_code}.')

    try:
        logger.info('Pollo 27 - Tentando extrair dados do site.')
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

        logger.info(f'Pollo 27 - Dados de {len(data)} produtos foram extraídos.')
    except Exception as e:
        logger.critical(f'Pollo 27 - Erro ao extrair dados: {e}.')
        data = []

    logger.info(f'Pollo 27 - Criando pandas.Dataframe com {len(data)} produtos.')

    df = (
        pd.DataFrame(data)
        .assign(
            valor_unitario = lambda x: x['valor_original']/x['quantidade']
        )
    )   

    return df

@logfire.instrument('Extraindo URLs do El Chañar!', record_return=True)
@st.cache_data(ttl = datetime.timedelta(hours=5), max_entries = 10, show_spinner = "Extraindo URL's do site El Chañar...") 
def get_urls():
    
    try:
        
        logger.info('El Chañar - Iniciando a extração de URLs do site.')

        r = requests.get('https://carneselchaniar.com.ar/shop', headers={'user-agent':UserAgent().get_random_user_agent()})
        urls = [i.find('a')['href'] for i in BeautifulSoup(r.text, 'html.parser').find('div', {'class':"row rubros products-big"}) if i != '\n']

        final_urls = {
            re.findall(r'https://carneselchaniar.com.ar/shop/rubros/[0-9]{1,2}/[0-9]{1,2}-(\w.*)', url)[0]: url 
            for url in urls
        }

        logger.info('El Chañar - Extração de URLs do site concluída com sucesso.')
        return final_urls
    
    except Exception as e:
        logger.critical(f'El Chañar - Ocorreu um erro ao extrair as URLs: {e}')
        return f'Erro: {e}'


@logfire.instrument('Extraindo dados do El Chañar!', record_return=True)
@st.cache_data(ttl = datetime.timedelta(hours=5), max_entries = 10, show_spinner = "Extraindo dados do site El Chañar...") 
def extracao_dados():
    '''
        ### Objetivo:
        - Extrair dados do preço de carne do site elchañar e concatenar com dados do site soychu
    '''
    
    cambio = get_cambio()['R$->$']
    urls_dict = get_urls()

    # LISTA PARA GUARDAR OS DADOS
    dados = []

    logger.info(f'El Chañar - Início da extração de dados de {len(urls_dict)} páginas.')

    for tipo, url in urls_dict.items():

        logger.info(f'El Chañar - Iniciando processamento dos dados da carne {tipo} na URL {url}.')

        # REQUISICAO
        response = requests.get(url, headers={'user-agent':UserAgent().get_random_user_agent()})

        produtos = BeautifulSoup(response.text, 'html.parser').find_all("div", class_=lambda c: c and "hidden sinmarca" in c)
        # nomes = [i.find('a', class_ = lambda c: c and 'text-decoration-none' in c).text for i in produtos]
        # precos = [(i.find('h3').text).strip() for i in produtos if i.find('h3') is not None]

        for i in produtos:
        
            logger.info(f"El Chañar - Processando dados da carne {tipo} na URL {url} - Produto {i.find('a', class_ = lambda c: c and 'text-decoration-none' in c).text}.")

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

        logger.info(f'El Chañar - Fim do processamento dos dados da carne {tipo} na URL {url}.')

    logger.info(f'El Chañar - Fim da extração de dados. {len(dados)} produtos encontrados.')

    # DATAFRAME EL CHAÑAR
    logger.info('El Chañar - Criação do pandas.Dataframe.')
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
    logger.info('Pollo 27 - Criação do pandas.Dataframe.')
    df_soychu = extract_data_soychu()

    # DATAFRAME FINAL
    logger.info('Criação do pandas.Dataframe com junção dos dados do El Chañar e Pollo 27.')
    columns = list(
        set(df_elchanar.columns).intersection(set(df_soychu.columns))
    )

    df_final = pd.concat(
        [df_elchanar[columns], df_soychu[columns]], 
        ignore_index=True
    )

    df_final[df_final.select_dtypes(include='float').columns] = df_final.select_dtypes(include='float').round(2)

    df_final = (
        df_final.assign(
            marca_carne = lambda df_: np.where(
                df_['marca_carne'] == 'EL CHAÑAR', 
                df_['marca_carne'], 
                'POLLO 27'
            ),
            tipo_carne = lambda df_: np.select(
                [
                    df_['tipo_carne'].str.contains('pollo', case=False, na=False),
                    df_['tipo_carne'].str.contains('carn', case=False, na=False),
                    df_['tipo_carne'].notna()
                ],
                [
                    'pollo',
                    'carniceria',
                    df_['tipo_carne']
                ],
                default=np.nan
            )
        )
        [[
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
    )

    logger.info('Criação do pandas.Dataframe finalizado.')

    # SALVANDO COMO PARQUET
    try:
        logger.info(f"Tentando salvar pandas.Dataframe como parquet no path {os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze')}.")
        pq.write_to_dataset(
            table = pa.Table.from_pandas(df_final),
            root_path = os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze'),
            partition_cols = ['ano','mes'],
            # partition_filename_cb = lambda x: '-'.join(x)+'.parquet', (Não funciona com o uso o use_legacy_dataset = False, que é necessário para usar o existing_data_behaviour)
            existing_data_behavior = 'delete_matching',
            use_legacy_dataset = False
        )
        logger.info(f"Dados salvos no path {os.path.join(os.getcwd(), 'data', 'bronze') if os.getcwd().__contains__('app') else os.path.join(os.getcwd(), 'app', 'data', 'bronze')}.")
    except Exception as e:
        logger.critical(f'Erro ao salvar o pandas.Dataframe como parquet: {e}.')
        pass

    return df_final

@logfire.instrument('Extraindo preços máximos e mínimos!', record_return=True)
@st.cache_data(ttl = datetime.timedelta(hours=5), max_entries = 10, show_spinner = "Extraindo preços mínimos e máximos...") 
def min_max_prices():
    
    # Obtendo os preços máximos e mínimos do dia atual
    try:
        logger.info('Tentando obter dados de preços máximos e mínimos.')

        df = extracao_dados()
        preco_min, preco_max = df.valor_original.min(), df.valor_original.max()

        logger.info(f'Preços mínimos e máximos extraídos com sucesso: {preco_min}, {preco_max}.')
        return preco_min, preco_max
    
    except Exception as e:
        logger.critical(f'Erro ao obter dados de preços máximos e mínimos: {e}.')
        return None, None