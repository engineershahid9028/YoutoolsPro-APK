import random
from passlib.context import CryptContext
from jose import jwt
from datetime import datetime,timedelta
from app.config import SECRET_KEY,ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM
pwd_context=CryptContext(schemes=['bcrypt'],deprecated='auto')
def hash_password(p): return pwd_context.hash(p)
def verify_password(p,h): return pwd_context.verify(p,h)
def generate_otp(): return str(random.randint(100000,999999))
def create_access_token(data):
 to_encode=data.copy()
 expire=datetime.utcnow()+timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
 to_encode.update({'exp':expire})
 return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)