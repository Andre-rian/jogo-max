import logging
from logging import FileHandler

NIVEL = logging.DEBUG
ARQUIVO_LOG = "jogo.log"

FORMATO = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DATA_FORMATO = "%H:%M:%S"


def configurar_logging():
    #FileHandler: um único arquivo de log (jogo.log), sem rotação jogo.log.1/2/3
    file_handler = FileHandler(
        ARQUIVO_LOG,
        mode="a",
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