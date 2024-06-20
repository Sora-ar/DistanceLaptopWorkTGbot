import sqlite3
from functools import wraps

MAX_SITES = 5


def conn_db(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        conn = sqlite3.connect('sites.db')
        cursor = conn.cursor()
        smth = func(cursor, *args, **kwargs)
        conn.commit()
        conn.close()
        return smth
    return wrapper


@conn_db
def add_site(cursor, url):
    cursor.execute('INSERT INTO sites (url) VALUES (?)', (url,))
    cursor.execute('DELETE FROM sites WHERE id NOT IN (SELECT id FROM sites ORDER BY id DESC LIMIT ?)', (MAX_SITES,))


@conn_db
def get_last_sites(cursor, limit=5):
    cursor.execute('SELECT url FROM sites ORDER BY id DESC LIMIT ?', (limit,))
    sites = cursor.fetchall()
    return [site[0] for site in sites]
