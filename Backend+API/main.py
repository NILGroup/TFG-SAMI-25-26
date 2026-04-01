# uvicorn main:app --reload

import uvicorn
from API import app
from loguru import logger
import os
import sys

# Crear carpeta de logs si no existe
os.makedirs("logs", exist_ok=True)
 
logger.add("logs/main.log", rotation="10 MB", retention="7 days", level="DEBUG",
           format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}")


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    uvicorn.run(app, host="127.0.0.1", port=5555)
