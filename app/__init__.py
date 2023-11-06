import logging

import redis
from telethon import TelegramClient

from app.config import api_id, api_hash, MYSQL_DB_CONNECTION
from app.db import register_datasource

session = None
def create_telegram_client() -> TelegramClient:


    global session
    # logging.getLogger('sqlalchemy.engine').setLevel(logging.ERROR)
    # 设置日志
    logging.basicConfig(format='%(asctime)s - %(pathname)s[line:%(lineno)d] - %(levelname)s:%(message)s',
                        level=logging.WARNING)

    redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

    logging.warning("create datasource start")
    session = register_datasource(MYSQL_DB_CONNECTION)
    logging.warning("create datasource finish\n")

    return TelegramClient('lee7s', api_id, api_hash, proxy=("socks5", '127.0.0.1', 7890))
    # return TelegramClient('lee7s', api_id, api_hash)