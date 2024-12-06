from jose import JWTError, jwt

# JWT 설정
SECRET_KEY = "as3k59vkl1k39e" # 임의 변경 가능
ALGORITHM = "HS256" # JWT 토큰 서명란, 해당 암호화 알고리즘 사용

# JWT 토큰 발급 시 데이터 변경
jwt_token_data = {
	"iss": "rabbitmq.test.com", # 토큰 발급자
	"sub": "chunjae-service005", # 사용자 고유 ID
	"role": "admin" 
}

# 토큰 검증 함수
def verify_token(token: str):
    try:
        jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  
    except Exception as e:
        print(f"Error: {e}")

# 토큰 요청 시, 해당 파일 실행하여 JWT 토큰 발급
if __name__ == "__main__":
    jwt_token = jwt.encode(jwt_token_data, SECRET_KEY, algorithm=ALGORITHM)
    print(jwt_token)
    verify_token(jwt_token)
    