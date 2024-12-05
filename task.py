from fastapi import HTTPException
from redis_get import wait_for_result, send_message
from models import ApiRequest
import yaml

##########################################
# YAML 파일 -> 딕셔너리 변환 함수
##########################################
def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)  
    return config


######################
# 전역변수 선언
######################
CONFIG = load_config()

##########################################
# task_id 에 따라 태스크 순차 실행
##########################################
async def execute_task(task_id: int, request: ApiRequest):

    task_step = CONFIG["tasks"].get(task_id)
    # 작업 결과 저장용 딕셔너리
    results = {}
    
    try:
    # 미리 사전에 작업할 것들을 다 정의해놓고, for문으로 반복하여 돌린다. 
        for step in task_step: 
            step_name = step["name"]
            queue_name = step["queue"]
            
            request_id = send_message(request, queue_name)
            result = await wait_for_result(request_id)
            results[step_name] = result
    
    except Exception as e:
        print(f"Error: {e}")

    return results




# redis_instance = RedisSingleton(REDIS_HOST, REDIS_PORT, db=0)


# ##################################################### 
# # Request ID 매핑하여 Result 반환
# ##################################################### 
# async def wait_for_result(request_id: str):
#     timeout = 10  # 최대 대기 시간 10초
#     interval = 0.05  # 폴링 간격 0.05초
#     elapsed_time = 0 # 경과 시간

#     while elapsed_time < timeout:
#         result = redis_instance.redis.get(request_id)
            
#         if result is not None:  # 결과가 있을 경우
#             redis_instance.redis.delete(request_id) # 결과값 저장했으면 삭제해도 됨.
#             return result
            
#         await asyncio.sleep(interval)  # interval 동안 대기
#         elapsed_time += interval  # 경과 시간 증가
            
#     raise HTTPException(status_code=504, detail="결과를 가져오는데 시간이 초과되었습니다.")
