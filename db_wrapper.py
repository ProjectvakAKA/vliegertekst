import os
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self):
        self.conn_string = os.environ.get('POSTGRES_URL')

    def execute(self, query, *params):
        conn = psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)
        cur = conn.cursor()

        try:
            cur.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
                conn.close()
                return result
            else:
                conn.commit()
                conn.close()
                return None
        except Exception as e:
            conn.close()
            raise e


db = Database()