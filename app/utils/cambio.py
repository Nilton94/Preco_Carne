import requests
from bs4 import BeautifulSoup
from random_user_agent.user_agent import UserAgent
import re
from .logger import get_logger
import logfire

# Criando logger
logger = get_logger()

@logfire.instrument('Retornando dados do câmbio!', record_return=True)
def get_cambio():

    try:
        logger.info('Iniciando a coleta de dados do câmbio')

        r = requests.get('https://wise.com/es/currency-converter/brl-to-ars-rate', headers={'user-agent':UserAgent().get_random_user_agent(), 'encoding': 'utf-8'})
        tag = BeautifulSoup(r.text, 'html.parser').find('h3', 'cc__source-to-target').text

        currency = re.findall(r'([\d,.]+)\s*([A-Za-z$]+)', tag)
        final = {f'{currency[0][1]}->{currency[1][1]}': float(currency[1][0].replace(',', '.'))}

        logger.info(f'Dados do câmbio coletados com sucesso: {final}')

        return final
    except requests.exceptions.RequestException as e:
        logger.error(f'Erro ao coletar dados do câmbio: {e}')
        logger.info('Retornando valor padrão para o câmbio')
        
        return {'R$->$': 200.0}
    except Exception as e:
        logger.error(f'Erro ao coletar dados do câmbio: {e}')
        logger.info('Retornando valor padrão para o câmbio')
        
        return {'R$->$': 200.0}