from fastapi import FastAPI, Query, HTTPException, status, Depends,Request
from task import execute_task
from redis_get import *
from models import *
from jwt import *
import json

app = FastAPI() 

########################################################
# API Gateway 진입점 API (태스크 관리 및 JWT 검증)
########################################################
@app.post("/")
async def api_gateway(request: Request, current_user: str = Depends(get_current_user)):
    try:
        results = await execute_task(request.task_id, request)
        return {"task_id": request.task_id, "results": results}

    except Exception as e:
        print(f"Error: {e}")
    
######################################################################
# 로그인 엔드포인트
######################################################################
@app.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = fake_users_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user["username"]})
    return {"access_token": access_token, "token_type": "bearer"}


#########################################################
# 직접 엔진 호출하는 API
# GET - 계산식 결과 호출
#########################################################
@app.get("/calc/")
async def calc(
    expression: str = Query(
        ..., 
        title="expression",
        description="Math Expression ( Support: +, - )",
        min_length=1,
        max_length=1000
        )
    ):

    request_id = send_message(expression, "calc_queue")
    
    result_json = await wait_for_result(request_id) 
    
    try:
        result = json.loads(result_json)
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="서버 내부 오류: 결과를 파싱할 수 없습니다.")
    
    if "error" in result:
        raise HTTPException(status_code=400, detail=result.get("error"))
    
    return {
        "request_id": request_id, 
        "expression": expression, 
        "result": result.get("result")
    }

#########################
# POST - 계산식 결과 호출
#########################
@app.post("/calc/")
async def calc(request: CalcRequest):
    request_id = send_message(request, "calc_queue")
    result = await wait_for_result(request_id)
    return {"request_id": request_id, "expression": request.expression, "result": result}

#########################
# POST - 번역 엔진 호출
#########################
@app.post("/trans")
async def translate(request: TransRequest):
    request_id = send_message(request, "trans_queue")
    result = await wait_for_result(request_id)
    return {"request_id": request_id, "text": request.text, "번역 결과": result}
    
#########################
# POST - 번역 엔진 호출
#########################
@app.post("/encrypt")
async def translate(request: EncryptRequest):
    request_id = send_message(request, "encrypt_queue")
    result = await wait_for_result(request_id)
    return {"request_id": request_id, "text": request.text, "암호화 결과": result}
