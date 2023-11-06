from datetime import datetime

from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, DateTime

# 基础类
BaseDB = declarative_base()

# 记录表
class Record(BaseDB):
    """必须继承BASE"""

    __tablename__ = "record"

    user_id = Column(String, primary_key=True, autoincrement=False, nullable=False)
    notice_group_id = Column(String, nullable=False)
    status = Column(Integer, default=0, nullable=False)
    token = Column(String, nullable=False)

    create_time = Column(DateTime, default=datetime.now, nullable=False)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)


    def __str__(self):
        return f"{self.user_id},{self.notice_group_id},{self.status},{self.token},{self.create_time},{self.update_time}"



# 通知包含表
class Include(BaseDB):
    """必须继承BASE"""

    __tablename__ = "include"


    id = Column(Integer, primary_key=True, autoincrement=True, nullable=False)
    user_id = Column(String, nullable=False)
    group_id = Column(String, nullable=False)
    include = Column(String, default=[], nullable=False)

    create_time = Column(DateTime, default=datetime.now, nullable=False)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
