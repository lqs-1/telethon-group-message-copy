from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker


def register_datasource(db_path: str) -> scoped_session:
    # 创建数据库引擎
    engine = create_engine(db_path, echo=True)
    # 绑定引擎
    return scoped_session(sessionmaker(bind=engine))
