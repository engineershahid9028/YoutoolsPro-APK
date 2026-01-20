from sqlalchemy import Column, BigInteger, Boolean, DateTime, Float, String, Integer, Index
from datetime import datetime
from db import Base


class User(Base):
    __tablename__ = "users"

    telegram_id = Column(BigInteger, primary_key=True, index=True)
    is_premium = Column(Boolean, default=False, index=True)
    premium_expiry = Column(DateTime, nullable=True)
    wallet = Column(Float, default=0.0)
    referrer_id = Column(BigInteger, nullable=True)
    is_banned = Column(Boolean, default=False, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class Payment(Base):
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    txid = Column(String, unique=True, index=True)
    amount = Column(Float)
    status = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class SupportTicket(Base):
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    message = Column(String)
    status = Column(String, default="open")
    created_at = Column(DateTime, default=datetime.utcnow)


class TicketReply(Base):
    __tablename__ = "ticket_replies"

    id = Column(Integer, primary_key=True)
    ticket_id = Column(Integer, index=True)
    admin_id = Column(BigInteger)
    reply = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)


class PromoCode(Base):
    __tablename__ = "promo_codes"

    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True, index=True)
    days = Column(Integer, default=30)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)


class ToolUsage(Base):
    __tablename__ = "tool_usage"

    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, index=True)
    tool = Column(String)
    query = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)