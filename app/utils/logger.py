import os
import logging
from logging.handlers import RotatingFileHandler
from dotenv import load_dotenv
import logfire
load_dotenv()

def get_logger(name: str = __name__, level: str = "info") -> logging.Logger:
    """Retorna um logger configurado para terminal e logfire com nível e formato especificados.

    Args:
        name (str, optional): Nome do logger. Default é __name__.
        level (str, optional): Nível do logger, com os valores possíveis "debug", "info", "warning", "error", "critical". Default é "info".

    Raises:
        ValueError: caso o nível de log não seja válido.

    Returns:
        logging.Logger: Logger configurado com o nível e formato especificados.
    """
    
    logfire.configure(
        token=os.environ['LOGFIRE_TOKEN'],
        # pydantic_plugin=logfire.PydanticPlugin(record='all'), # dados de validação do pydantic - Deprecado
        console = False # Evita printar no console, já que para isso temos o StreamHandler
    )
    logfire.instrument_pydantic()
    logfire.instrument_requests()
    logfire.instrument_system_metrics()

    # Mapeamento de níveis de log
    level_map = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "critical": logging.CRITICAL
    }

    # Limpa a string e tenta converter
    level_clean = level.strip().lower()
    try:
        log_level = level_map[level_clean]
    except KeyError:
        raise ValueError(
            f"Nível de log inválido: '{level}'. Use um dos valores: {list(level_map.keys())}"
        )

    # Limpa e converte o nível informado
    level_clean = level.strip().lower()
    log_level = level_map.get(level_clean, logging.INFO)  # default = INFO

    # Diretório do projeto e dos logs
    current_script_path = os.path.abspath(__file__)
    app_directory = os.path.dirname(os.path.dirname(current_script_path))
    log_dir = os.path.join(app_directory, 'logs')
    os.makedirs(log_dir, exist_ok=True)

    log_file_path = os.path.join(log_dir, 'app.log')

    logger = logging.getLogger(name)
    logger.setLevel(log_level)

    if not logger.handlers:
        formatter = logging.Formatter(
            '[%(asctime)s] - %(levelname)s - %(funcName)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )

        # LOGGER PODE TER VÁRIOS HANDLERS, QUE SÃO OS RESPONSÁVEIS POR ENVIAR AS MENSAGENS PARA O DESTINO
        #   * StreamHandler: Envia mensagens para o console (terminal)
        #   * FileHandler: Envia mensagens para um arquivo
        #   * SMTPHandler: Envia mensagens por e-mail
        #   * HTTPHandler: Envia mensagens para um servidor HTTP
        #   * SysLogHandler: Envia mensagens para um servidor SysLog
        #   * NTEventLogHandler: Envia mensagens para o log de eventos do Windows
        #   * LogfireLoggingHandler: Envia mensagens para o Logfire

        # Terminal
        stream_handler = logging.StreamHandler()
        stream_handler.setFormatter(formatter)
        stream_handler.setLevel(log_level)
        logger.addHandler(stream_handler)

        # Logfire
        logfire_handler = logfire.LogfireLoggingHandler()
        logger.addHandler(logfire_handler)

        # Arquivo com rotação - Limita o tamanho do arquivo a 1MB e mantém 5 backups
        file_handler = RotatingFileHandler(
            log_file_path,
            maxBytes=1_000_000,
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        file_handler.setLevel(log_level)
        logger.addHandler(file_handler)

    return logger