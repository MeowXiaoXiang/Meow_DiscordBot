from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class EmojiInfo(Base):
    __tablename__ = 'emoji_info'
    key = Column(Integer, primary_key=True, unique=True)
    value = Column(Integer)

class DatabaseSession:
    def __init__(self, session_factory):
        self.session_factory = session_factory
        self.session = None

    def __enter__(self):
        self.session = self.session_factory()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

def connect_db():
    '''
    連接到名為 'emoji_database.db' 的 SQLite 資料庫，並創建表格（如果該表格尚未存在）。
    返回：
        DatabaseSession：支援上下文管理器協議的資料庫會話類別，可以用於後續的資料庫操作。
    '''
    engine = create_engine('sqlite:///emoji_database.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return DatabaseSession(Session)

def set_key(session, key, value):
    '''
    在 'emoji_info' 表格中設置一個key:value。
    參數：
        session：資料庫會話對象。
        key：要設置的鍵。
        value：要設置的值。
    返回：
        無
    '''
    emoji = session.query(EmojiInfo).filter_by(key=key).first()
    if emoji:
        emoji.value = value
    else:
        emoji = EmojiInfo(key=key, value=value)
        session.add(emoji)
    session.commit()

def get_key(session, key):
    '''
    從 'emoji_info' 表格中獲取指定key的value。
    參數：
        session：資料庫會話對象。
        key：要獲取的鍵。
    返回：
        value：key對應的值。如果該key不存在，則返回 None。
    '''
    emoji = session.query(EmojiInfo).filter_by(key=key).first()
    return emoji.value if emoji else None

def get_all_emoji_info(session):
    '''
    從 'emoji_info' 表格中獲取所有的表情符號資訊。
    參數：
        session：資料庫會話對象。
    返回：
        rows：一個包含所有表情符號資訊的列表。每個元素都是一個包含key:value的元組。
    '''
    emojis = session.query(EmojiInfo).all()
    return [(emoji.key, emoji.value) for emoji in emojis]

def delete_all(session):
    '''
    刪除 'emoji_info' 表格中的所有資料。
    參數：
        session：資料庫會話對象。
    返回：
        無
    '''
    session.query(EmojiInfo).delete()
    session.commit()