from pydantic import BaseModel,EmailStr
class Signup(BaseModel): email:EmailStr; password:str
class Login(BaseModel): email:EmailStr; password:str
class OTPVerify(BaseModel): email:EmailStr; otp:str
class Token(BaseModel): access_token:str; token_type:str