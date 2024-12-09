import redis
from threading import Lock
##########################################
# CallBack 함수
# 설명 : 계산엔진을 통해 결과값을 전달받음
##########################################
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
    
redis_instance = RedisSingleton(host='localhost', port=6379, db=0)
# 싱글톤 확인 print(redis_instance is redis_instance2)

##########################################
# Redis에 결과값 저장
##########################################
def set_result(request_id, result):
    global redis_instance
    while(True):   
        try:
            if not redis_instance.redis.ping():
                print("Redis 재연결 시도 중 ...")
                redis_instance = RedisSingleton(host='localhost', port=6379, db=0)
            
            redis_instance.redis.set(request_id, result, ex=60)
            value = redis_instance.redis.get(request_id)
            print(f"redis 값 저장 완료 {request_id} = {value}")
            break
        
        except Exception as e:
            print(f"Error: {e}") 
