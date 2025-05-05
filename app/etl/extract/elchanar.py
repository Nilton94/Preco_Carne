import pandas as pd
import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
import re
import datetime
import pytz
import streamlit as st
from app.utils.cambio import get_cambio
from app.utils.logger import get_logger

logger = get_logger(level='debug')

# Cacheando os dados carregados, com permanência de 5 hs (18000 s) e máximo de 10 entradas
@st.cache_data(ttl = 18000, max_entries = 10)
def get_urls_elchanar():
    """Retorna as URLs de cada tipo de carne do site elchañar.

    Returns:
        Dict: Retorna um dicionário com as URLs de cada tipo de carne do site elchañar.
    """
    
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


@st.cache_data(ttl = 18000, max_entries = 10)
def data_extraction_elchanar():
    """Retorna os dados de preços de carne do site el chañar.

    Returns:
        pandas.Dataframe: Retorna um dataframe com os dados de preços de carne do site el chañar.
    """
    
    logger.info('El Chañar - Extração dos dados de câmbio e URLs.')
    cambio = get_cambio()['R$->$']
    urls_dict = get_urls_elchanar()

    # LISTA PARA GUARDAR OS DADOS
    dados = []

    logger.info('El Chañar - Início da extração de dados.')
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

    return df_elchanar