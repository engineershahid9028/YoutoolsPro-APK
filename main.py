from sqlalchemy import text
from db import SessionLocal


@app.get("/admin/migrate-users")
def migrate_users():
    db = SessionLocal()

    users = db.execute(text("SELECT telegram_id FROM users WHERE id IS NULL")).fetchall()

    counter = 1
    for u in users:
        db.execute(
            text("UPDATE users SET id = :id WHERE telegram_id = :tg"),
            {"id": counter, "tg": u.telegram_id}
        )
        counter += 1

    db.commit()
    db.close()

    return {"status": "migration_done", "users_updated": counter - 1}