from threading import Lock
import redis

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
    
