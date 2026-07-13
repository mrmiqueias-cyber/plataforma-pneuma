import sqlite3

try:
    conn = sqlite3.connect('casulo.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM experts')
    rows = cursor.fetchall()
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Database error: {e}")
finally:
    if conn:
        conn.close()