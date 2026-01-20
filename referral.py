from db import cursor, conn

def apply_referral(user_id, amount):
    cursor.execute("SELECT referred_by FROM users WHERE id=%s", (user_id,))
    ref = cursor.fetchone()[0]

    if ref:
        commission = amount * 0.10
        cursor.execute("UPDATE users SET wallet = wallet + %s WHERE id=%s", (commission, ref))
        cursor.execute(
            "INSERT INTO referrals(referrer_id,referred_id,commission) VALUES(%s,%s,%s)",
            (ref, user_id, commission)
        )
        conn.commit()
