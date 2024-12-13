from fastapi import HTTPException
from models import ApiRequest
from rabbitmq_client import *
from redis_client import *
import yaml
import uuid
import json
import asyncio
import os

###########################################
#                변수 선언                 #
###########################################
RABBIT_HOST = os.getenv("RABBIT_HOST")
RABBIT_PORT = os.getenv("RABBIT_PORT")
RABBIT_USERNAME = os.getenv("RABBIT_USERNAME")
RABBIT_PASSWORD = os.getenv("RABBIT_PASSWORD")
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = os.getenv("REDIS_PORT")

##########################################
# YAML 파일 -> 딕셔너리 변환 함수
##########################################
def load_config():
    with open("config.yaml", "r") as file:
        config = yaml.safe_load(file)  
    return config

CONFIG = load_config()

##########################################
# task_id 에 따라 태스크 순차 실행
##########################################
async def execute_task(request: ApiRequest):

    task_step = CONFIG["tasks"].get(request.task_id)
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

###################################################### 
# RabbitMQ 메시지 퍼블리싱 
######################################################
rabbitmq_instance = RabbitMQSingleton(host=RABBIT_HOST, username=RABBIT_USERNAME, password=RABBIT_PASSWORD)

def send_message(request, queue_name: str):
    global rabbitmq_instance
    while(True):
        try:
            request_id = str(uuid.uuid4())
            
            message = json.dumps({
                     "request_id": request_id,
                     "text": request.text,
                     "expression": request.expression,
                     "direction": request.direction
                 }).encode()
                
            # 연결이 정상적인지 확인
            if rabbitmq_instance.connection.is_open:
                # 채널도 정상적인지 확인, 모두 정상이면 퍼블리싱
                if rabbitmq_instance.channel.is_open:
                    rabbitmq_instance.queue_publish(message, queue_name)
                # 채널이 열려있지 않을 경우 채널만 재연결  
                else:
                    rabbitmq_instance.open_channel()
            # 연결 비정상일 시, 인스턴스 재생성 및 커넥션 / 채널 생성
            else:
                rabbitmq_instance = RabbitMQSingleton(host=RABBIT_HOST, username=RABBIT_USERNAME, password=RABBIT_PASSWORD)
                rabbitmq_instance._connect(host=RABBIT_HOST, username=RABBIT_USERNAME, password=RABBIT_PASSWORD)
                print(f"rabbitmq connection is reconnected !!!")   
                
            return request_id
        
        except Exception as e:
            print(f"Error: {e}")


###################################################### 
# Redis GET
######################################################
redis_instance = RedisSingleton(host=REDIS_HOST, port=REDIS_PORT, db=0)

async def wait_for_result(request_id: str):
    global redis_instance
    
    timeout = 10  # 최대 대기 시간 10초
    interval = 0.05  # 폴링 간격 0.05초
    elapsed_time = 0 # 경과 시간

    while elapsed_time < timeout:
        try:
            result = redis_instance.redis.get(request_id)
                
            if result is not None:  # 결과가 있을 경우
                redis_instance.redis.delete(request_id) # 결과값 저장했으면 삭제해도 됨.
                return result
        
        except redis.ConnectionError as e:
            print(f"Redis 연결 실패: {e}. 재시도 중...")
            # 연결에 실패하면 재시도 진행
            redis_instance = RedisSingleton(host=REDIS_HOST, port=REDIS_PORT, db=0)
            
        await asyncio.sleep(interval)  # interval 동안 대기
        elapsed_time += interval  # 경과 시간 증가
            
    raise HTTPException(status_code=504, detail="결과를 가져오는데 시간이 초과되었습니다.")
