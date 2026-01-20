from db import cursor, conn

def add_wallet(user_id, amount):
    cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id=%s", (amount, user_id))
    conn.commit()

def get_wallet(user_id):
    cursor.execute("SELECT wallet FROM users WHERE id=%s", (user_id,))
    return cursor.fetchone()[0]
