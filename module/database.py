import sqlite3

def connect_db():
    '''
    連接到名為 'emoji_database.db' 的 SQLite 資料庫，並創建一個名為 'emoji_info' 的表格（如果該表格尚未存在）。
    表格有兩個欄位：'key' 和 'value'。

    返回：
        conn：資料庫連接對象，可以用於後續的資料庫操作。
    '''
    conn = sqlite3.connect('emoji_database.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS emoji_info (key text unique, value text)')
    conn.commit()
    return conn

def set_key(conn, key, value):
    '''
    在 'emoji_info' 表格中設置一個鍵值對。

    參數：
        conn：資料庫連接對象。
        key：要設置的鍵。
        value：要設置的值。

    返回：
        無
    '''
    c = conn.cursor()
    c.execute('INSERT OR REPLACE INTO emoji_info VALUES (?,?)', (key, value))
    conn.commit()

def get_key(conn, key):
    '''
    從 'emoji_info' 表格中獲取指定鍵的值。

    參數：
        conn：資料庫連接對象。
        key：要獲取的鍵。

    返回：
        value：鍵對應的值。如果該鍵不存在，則返回 None。
    '''
    c = conn.cursor()
    c.execute('SELECT value FROM emoji_info WHERE key=?', (key,))
    return c.fetchone()

def get_all_emoji_info(conn):
    '''
    從 'emoji_info' 表格中獲取所有的表情符號資訊。

    參數：
        conn：資料庫連接對象。

    返回：
        rows：一個包含所有表情符號資訊的列表。每個元素都是一個包含鍵和值的元組。
    '''
    c = conn.cursor()
    c.execute('SELECT * FROM emoji_info')
    return c.fetchall()

def delete_all(conn):
    '''
    刪除 'emoji_info' 表格中的所有資料。

    參數：
        conn：資料庫連接對象。

    返回：
        無
    '''
    c = conn.cursor()
    c.execute('DELETE FROM emoji_info')
    conn.commit()