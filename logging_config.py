import logging
from logging.handlers import RotatingFileHandler

NIVEL = logging.DEBUG
ARQUIVO_LOG = "jogo.log"

FORMATO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATA_FORMATO = "%H:%M:%S"


def configurar_logging():
    # RotatingFileHandler: o log cresce até MAX_BYTES e rotaciona para
    # jogo.log.1, jogo.log.2 ... em vez de ser sobrescrito a cada execução.
    file_handler = RotatingFileHandler(
        ARQUIVO_LOG,
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )

    logging.basicConfig(
        level=NIVEL,
        format=FORMATO,
        datefmt=DATA_FORMATO,
        handlers=[
            logging.StreamHandler(),
            file_handler,
        ],
        force=True,
    )