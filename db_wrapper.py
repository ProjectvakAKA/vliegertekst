import os
import psycopg2
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self):
        self.conn_string = os.environ.get('POSTGRES_URL')

        if not self.conn_string:
            raise ValueError(
                "POSTGRES_URL environment variabele is niet ingesteld!"
            )

    def execute(self, query, *params):
        try:
            conn = psycopg2.connect(self.conn_string, cursor_factory=RealDictCursor)
            cur = conn.cursor()

            cur.execute(query, params)

            if query.strip().upper().startswith('SELECT'):
                result = cur.fetchall()
            else:
                conn.commit()
                result = None

            cur.close()
            conn.close()
            return result

        except psycopg2.OperationalError as e:
            raise ValueError(f"Database connectie fout: {str(e)}")
        except Exception as e:
            raise


db = Database()