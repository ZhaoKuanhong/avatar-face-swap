import sqlite3
from flask import g
import os
from lib.common.constants import DATABASE

# 默认数据库文件名，可根据实际项目配置


def get_db():
    """获取数据库连接，使用 Flask 的 g 对象缓存连接"""
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row  # 支持 dict-like 访问行数据
    return db

def query_db(query, args=(), one=False):
    """执行 SELECT 查询"""
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv

def execute_db(query, args=()):
    """执行 INSERT、UPDATE、DELETE 等写操作"""
    db = get_db()
    cur = db.execute(query, args)
    db.commit()
    return cur.lastrowid

def init_db():
    """初始化数据库，例如建表"""
    with open(os.path.join(os.path.dirname(__file__), 'schema.sql'), 'r') as f:
        get_db().executescript(f.read())
        get_db().commit()

def close_connection(exception):
    """关闭数据库连接，注册给 Flask 的 teardown_appcontext"""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()