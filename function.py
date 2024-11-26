import redis
import asyncio
import uuid
import json
from __init__ import *
from fastapi import HTTPException

###########################################
#                 Function                #
###########################################

rabbitmq_singleton = RabbitMQSingleton(host=RABBITMQ_HOST, username=USERNAME, password=PASSWORD, queue="calc_queue") 
   
r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, db=0)

##################################################### 
# FastAPI -> RabbitMQ 연동 및 큐 전송 
##################################################### 
def send_message(expression: str, queue_name: str):
    request_id = str(uuid.uuid4())

    # JSON Serialize 
    message = json.dumps({
        "request_id": request_id,
        "expression": expression
    }).encode()
    
    # 이미 채널은 열려있지만, 혹여나 Timeout / 장애 시 Channel이 닫힐 경우 재연결
    rabbitmq_singleton.open_channel(queue_name)
    
    rabbitmq_singleton.queue_publish(queue_name, message)

    return request_id

##################################################### 
# Request ID 매핑하여 Result 반환
##################################################### 
async def wait_for_result(request_id: str):
    timeout = 10  # 최대 대기 시간 10초
    interval = 0.05  # 폴링 간격 0.05초
    elapsed_time = 0 # 경과 시간

    while elapsed_time < timeout:
        result = r.get(request_id)
            
        if result is not None:  # 결과가 있을 경우
            r.delete(request_id) # 결과값 저장했으면 삭제해도 됨.
            return result
            
        await asyncio.sleep(interval)  # interval 동안 대기
        elapsed_time += interval  # 경과 시간 증가
            
    raise HTTPException(status_code=504, detail="결과를 가져오는데 시간이 초과되었습니다.")
