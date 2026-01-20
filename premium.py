from datetime import datetime, timedelta
from db import cursor, conn

def activate_premium(user_id, days=30):
    expiry = datetime.now() + timedelta(days=days)

    cursor.execute("""
        UPDATE users SET is_premium=true, premium_expiry=%s WHERE id=%s
    """, (expiry, user_id))
    conn.commit()

def check_premium(user_id):
    cursor.execute("SELECT is_premium, premium_expiry FROM users WHERE id=%s", (user_id,))
    row = cursor.fetchone()

    if not row:
        return False

    is_premium, expiry = row

    if not is_premium:
        return False

    if datetime.now() > expiry:
        cursor.execute("UPDATE users SET is_premium=false WHERE id=%s", (user_id,))
        conn.commit()
        return False

    return True
