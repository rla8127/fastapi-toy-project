from fastapi import FastAPI, Query, HTTPException
from function import *

app = FastAPI() 

#########################
# GET - 계산식 결과 호출
#########################
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
    request_id = send_message(request.expression, "calc_queue")
    result = await wait_for_result(request_id)
    return {"request_id": request_id, "expression": request.expression, "result": result}

#@app.post("/")
#async def api_gateway(request : d):
#    1.JWT 토큰인증
#    2. 테스크 판별 -> 그걸 순서대로 실행
    
#    3. "abc" -> md5 -> "asdkaopsdkasp" 
    
#    "asdasjicxoijojdoasjdoijasodjaosdjo"