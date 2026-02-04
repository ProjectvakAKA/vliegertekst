import os
from cs50 import SQL

# Check of we op Vercel draaien (met PostgreSQL) of lokaal (met SQLite)
if os.environ.get('POSTGRES_URL'):
    # Op Vercel - gebruik Supabase PostgreSQL
    db = SQL(os.environ.get('POSTGRES_URL'))
else:
    # Lokaal - gebruik SQLite
    db = SQL("sqlite:///11.db")