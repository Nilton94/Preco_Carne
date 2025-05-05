from abc  import ABC, abstractmethod
from typing import List, Dict

class Extract(ABC):
    """Classe abstrata para a extração de dados de diferentes fontes.
    
    Atributos:
        urls (Dict): Dicionário contendo as URLs a serem extraídas.
    """
    
    def __init__(self, urls: List[str]):
        self.urls = urls
    
    @abstractmethod
    def extract_data(self) -> List[Dict]:
        """Método abstrato para extrair dados de uma fonte específica.
        
        Retorna:
            List[Dict]: Lista de dicionários contendo os dados extraídos.
        """
        pass