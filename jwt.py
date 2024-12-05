from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

# JWT 설정
SECRET_KEY = "as3k59vkl1k39e"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# OAuth2 설정
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# 유저 데이터 (데모용)
fake_users_db = {
    "chunjae": {
        "username": "chunjae",
        "password": "chunjae",  
    }
}

# 토큰 생성 함수
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy() # 데이터 복사, 원본 데이터 변경 방지
    expire = datetime.now() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))     
    to_encode.update({"exp": expire}) # 딕셔너리 Key-Value 추가 
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# 토큰 검증 함수
def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub") 
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return username
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

# 종속성: 토큰 검증
def get_current_user(token: str = Depends(oauth2_scheme)):
    return verify_token(token) # 토큰을 검증하여 username을 반환함. 

######################################################################
# 보호된 엔드포인트 -- 검증 목적으로 사용하였음
######################################################################
# @app.get("/protected")
# def protected_route(current_user: str = Depends(get_current_user)):
#     return {"message": f"Hello, {current_user}! This is a protected route."}
