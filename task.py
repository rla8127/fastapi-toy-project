from fastapi import HTTPException
from redis_get import wait_for_result, send_message
from models import ApiRequest
import yaml

##########################################
# YAML 설정 파일 
##########################################
def load_config(file_path="config.yaml"):
    with open(file_path, "r") as file:
        config = yaml.safe_load(file) # YAML 파일 -> Python 딕셔너리 변환
    return config 

######################
# 전역변수 선언
######################
CONFIG = load_config()

##########################################
# task_id 에 따라 태스크 순차 실행
##########################################
async def execute_task(task_id: int, request: ApiRequest):
    # 작업 리스트 가져오기
    task_step = CONFIG["tasks"].get(task_id)

    # 작업 결과 저장용 딕셔너리
    results = {}
    
    # 미리 사전에 작업할 것들을 다 정의해놓고, for문으로 반복하여 돌린다. 
    for step in task_step: 
        step_name = step["name"]
        queue_name = step["queue"]
        # 작업 순차 실행
        if step_name == "calc":
            request_id = send_message(request, queue_name) 
            result = await wait_for_result(request_id)
            results["calc"] = result
                
        elif step_name == "trans":
            request_id = send_message(request, queue_name)  
            result = await wait_for_result(request_id)
            results["trans"] = result

        elif step_name == "encrypt":
            request_id = send_message(request, queue_name) 
            result = await wait_for_result(request_id)
            results["encrypt"] = result

        else:
            raise HTTPException(status_code=500, detail=f"Unknown step: {step}")

    return results
