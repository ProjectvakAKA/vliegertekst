import sqlite3

# Connect to SQLite database (it will create a new database if it does not exist)
conn = sqlite3.connect('11.db')

# Create a cursor object to interact with the database
cursor = conn.cursor()
cursor.execute('PRAGMA foreign_keys = ON;')
# Create a new table
cursor.execute('''
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    password TEXT
)
''')

cursor.execute('''
CREATE TABLE contacts (
    user_id INTEGER,
    contact_ID TEXT,
    contact_name TEXT,
    contact_phone TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
)
''')
cursor.execute('''
CREATE TABLE messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sender_id INTEGER,
    receiver_id INTEGER,
    message_text TEXT,
    timestamp TEXT,
    FOREIGN KEY (sender_id) REFERENCES users(id),
    FOREIGN KEY (receiver_id) REFERENCES users(id)
)
''')



# Commit the transaction
conn.commit()

# Close the connection
conn.close()

print("Database created and table initialized.")