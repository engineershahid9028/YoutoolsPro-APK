from db import SessionLocal
from models import (
    User,
    Payment,
    SupportTicket,
    TicketReply,
    PromoCode,
    ToolUsage
)
from datetime import datetime, timedelta


# =========================
# DB SESSION HELPER
# =========================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# =========================
# USER SYSTEM
# =========================

def get_or_create_user(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()

    if not user:
        user = User(telegram_id=user_id)
        db.add(user)
        db.commit()
        db.refresh(user)

    db.close()
    return user


def get_all_users():
    db = SessionLocal()
    users = db.query(User).order_by(User.created_at.desc()).all()
    db.close()
    return users


def is_banned(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()
    db.close()
    return bool(user and user.is_banned)


# =========================
# PREMIUM SYSTEM
# =========================

def set_premium(user_id, days=30):
    db = SessionLocal()
    user = get_or_create_user(user_id)

    user.is_premium = True
    user.premium_expiry = datetime.utcnow() + timedelta(days=days)

    db.merge(user)
    db.commit()
    db.close()


def revoke_premium(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()

    if user:
        user.is_premium = False
        user.premium_expiry = None
        db.commit()

    db.close()


def is_premium(user_id):
    db = SessionLocal()
    user = db.query(User).filter(User.telegram_id == user_id).first()

    if not user or not user.is_premium:
        db.close()
        return False

    if user.premium_expiry and user.premium_expiry < datetime.utcnow():
        user.is_premium = False
        db.commit()
        db.close()
        return False

    db.close()
    return True


# =========================
# WALLET SYSTEM
# =========================

def add_wallet(user_id, amount):
    db = SessionLocal()
    user = get_or_create_user(user_id)

    user.wallet += float(amount)
    db.merge(user)
    db.commit()
    db.close()


# =========================
# PAYMENT SYSTEM
# =========================

def log_payment(user_id, txid, amount, status="success"):
    db = SessionLocal()

    # Prevent duplicate TXID
    exists = db.query(Payment).filter(Payment.txid == txid).first()
    if exists:
        db.close()
        return False

    payment = Payment(
        user_id=user_id,
        txid=txid,
        amount=amount,
        status=status
    )

    db.add(payment)
    db.commit()
    db.close()
    return True


def get_all_payments():
    db = SessionLocal()
    payments = db.query(Payment).order_by(Payment.created_at.desc()).all()
    db.close()
    return payments


def get_user_payments(user_id):
    db = SessionLocal()
    payments = db.query(Payment).filter(Payment.user_id == user_id).order_by(Payment.created_at.desc()).all()
    db.close()
    return payments


# =========================
# SUPPORT SYSTEM
# =========================

def create_ticket(user_id, message):
    db = SessionLocal()

    ticket = SupportTicket(
        user_id=user_id,
        message=message,
        status="open"
    )

    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    db.close()

    return ticket


def get_open_tickets():
    db = SessionLocal()
    tickets = db.query(SupportTicket).filter(
        SupportTicket.status == "open"
    ).order_by(SupportTicket.created_at.desc()).all()
    db.close()
    return tickets


def get_ticket(ticket_id):
    db = SessionLocal()
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    db.close()
    return ticket


def reply_ticket(ticket_id, admin_id, reply):
    db = SessionLocal()

    reply_obj = TicketReply(
        ticket_id=ticket_id,
        admin_id=admin_id,
        reply=reply
    )

    db.add(reply_obj)
    db.commit()
    db.close()


def close_ticket(ticket_id):
    db = SessionLocal()
    ticket = db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()

    if ticket:
        ticket.status = "closed"
        db.commit()

    db.close()
    return ticket


def get_ticket_replies(ticket_id):
    db = SessionLocal()
    replies = db.query(TicketReply).filter(
        TicketReply.ticket_id == ticket_id
    ).order_by(TicketReply.created_at.asc()).all()
    db.close()
    return replies


# =========================
# PROMO SYSTEM
# =========================

def create_promo(code, days=30):
    db = SessionLocal()

    promo = PromoCode(
        code=code.upper(),
        days=days,
        is_active=True
    )

    db.add(promo)
    db.commit()
    db.close()


def get_promo(code):
    db = SessionLocal()
    promo = db.query(PromoCode).filter(
        PromoCode.code == code.upper(),
        PromoCode.is_active == True
    ).first()
    db.close()
    return promo


def disable_promo(code):
    db = SessionLocal()
    promo = db.query(PromoCode).filter(PromoCode.code == code.upper()).first()

    if promo:
        promo.is_active = False
        db.commit()

    db.close()


# =========================
# ANALYTICS SYSTEM
# =========================

def log_tool_usage(user_id, tool, query):
    db = SessionLocal()

    usage = ToolUsage(
        user_id=user_id,
        tool=tool,
        query=query
    )

    db.add(usage)
    db.commit()
    db.close()


def get_total_requests():
    db = SessionLocal()
    total = db.query(ToolUsage).count()
    db.close()
    return total


def get_stats():
    db = SessionLocal()

    users = db.query(User).count()
    premium = db.query(User).filter(User.is_premium == True).count()
    wallets = sum(u.wallet for u in db.query(User).all())
    total_requests = db.query(ToolUsage).count()

    db.close()
    return users, premium, wallets, total_requests