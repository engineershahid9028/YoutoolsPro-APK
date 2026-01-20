from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app import schemas,models,utils
router=APIRouter(prefix='/auth',tags=['Auth'])
def get_db():
 db=SessionLocal();
 try: yield db
 finally: db.close()
@router.post('/signup')
def signup(data:schemas.Signup,db:Session=Depends(get_db)):
 user=db.query(models.User).filter(models.User.email==data.email).first()
 if user: raise HTTPException(400,'Email exists')
 otp=utils.generate_otp(); hashed=utils.hash_password(data.password)
 new=models.User(email=data.email,password=hashed,otp_code=otp,is_verified=False)
 db.add(new); db.commit(); print('OTP:',otp)
 return {'message':'Verify OTP'}
@router.post('/verify-otp')
def verify(data:schemas.OTPVerify,db:Session=Depends(get_db)):
 user=db.query(models.User).filter(models.User.email==data.email).first()
 if not user or user.otp_code!=data.otp: raise HTTPException(400,'Invalid OTP')
 user.is_verified=True; user.otp_code=None; db.commit(); return {'message':'Verified'}
@router.post('/login',response_model=schemas.Token)
def login(data:schemas.Login,db:Session=Depends(get_db)):
 user=db.query(models.User).filter(models.User.email==data.email).first()
 if not user or not utils.verify_password(data.password,user.password): raise HTTPException(401,'Invalid credentials')
 if not user.is_verified: raise HTTPException(403,'Verify account')
 token=utils.create_access_token({'sub':user.email}); return {'access_token':token,'token_type':'bearer'}