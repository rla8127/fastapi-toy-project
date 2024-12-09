from fastapi import FastAPI, Request
from models import *
from utils import *
from jwt_utils import verify_token

app = FastAPI() 

################################################################
# API Gateway 진입점 API (태스크 관리 및 JWT 검증)
################################################################
@app.post("/")
async def api_gateway(request: ApiRequest):
    try:
        verify_token(request.jwt_token)
        results = await execute_task(request)
        return {"task_id": request.task_id, "results": results}

    except Exception as e:
        print(f"Error: {e}")

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
