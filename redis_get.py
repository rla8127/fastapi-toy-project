from fastapi import FastAPI, Query, HTTPException
from rabbitmq_publish import *
import redis
import asyncio

###########################################
#          Variable Definition            #
###########################################
REDIS_HOST = "localhost"
REDIS_PORT = 6379

###########################################
#                 Function                #
###########################################
  
class RedisSingleton:
    _instance = None
    _lock = Lock() # Lock 객체 생성
    
    def __new__(cls, host, port, db):
        if not cls._instance: # 이미 인스턴스가 있다면 해당 인스턴스 제공
            with cls._lock: # Lock을 통해 해당 작업 시, 하나의 쓰레드만 동작
                if not cls._instance:
                    cls._instance = super().__new__(cls) # new는 메모리 할당
                    cls._instance.redis = redis.Redis(host=host, port=port, db=db)
        return cls._instance
    
redis_instance = RedisSingleton(REDIS_HOST, REDIS_PORT, db=0)


##################################################### 
# Request ID 매핑하여 Result 반환
##################################################### 
async def wait_for_result(request_id: str):
    timeout = 10  # 최대 대기 시간 10초
    interval = 0.05  # 폴링 간격 0.05초
    elapsed_time = 0 # 경과 시간

    while elapsed_time < timeout:
        result = redis_instance.redis.get(request_id)
            
        if result is not None:  # 결과가 있을 경우
            redis_instance.redis.delete(request_id) # 결과값 저장했으면 삭제해도 됨.
            return result
            
        await asyncio.sleep(interval)  # interval 동안 대기
        elapsed_time += interval  # 경과 시간 증가
            
    raise HTTPException(status_code=504, detail="결과를 가져오는데 시간이 초과되었습니다.")
