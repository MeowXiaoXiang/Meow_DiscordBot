from sqlalchemy import create_engine, Column, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()

class EmojiInfo(Base):
    __tablename__ = 'emoji_info'
    key = Column(Integer, primary_key=True, unique=True)
    value = Column(Integer)

def connect_db():
    '''
    連接到名為 'emoji_database.db' 的 SQLite 資料庫，並創建表格（如果該表格尚未存在）。
    返回：
        Session：資料庫會話類別，可以用於後續的資料庫操作。
    '''
    engine = create_engine('sqlite:///emoji_database.db')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    return Session

def set_key(session, key, value):
    '''
    在 'emoji_info' 表格中設置一個鍵值對。
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
    從 'emoji_info' 表格中獲取指定鍵的值。
    參數：
        session：資料庫會話對象。
        key：要獲取的鍵。
    返回：
        value：鍵對應的值。如果該鍵不存在，則返回 None。
    '''
    emoji = session.query(EmojiInfo).filter_by(key=key).first()
    return emoji.value if emoji else None

def get_all_emoji_info(session):
    '''
    從 'emoji_info' 表格中獲取所有的表情符號資訊。
    參數：
        session：資料庫會話對象。
    返回：
        rows：一個包含所有表情符號資訊的列表。每個元素都是一個包含鍵和值的元組。
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