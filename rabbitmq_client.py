from threading import Lock
import pika

###########################################
#          Variable Definition            #
###########################################
HOST_NAME = "172.16.10.237"
USERNAME = "fastapi_user" 
PASSWORD = "fastapi_user"

##########################################
# RabbitMQ 싱글톤 객체 정의
##########################################
class RabbitMQSingleton:
    _instance = None 
    _lock = Lock()   
    
    def __new__(cls, host, username, password):
        if not cls._instance: 
            with cls._lock:
                if not cls._instance:
                    cls._instance = super().__new__(cls) 
                    cls._instance._connect(host, username, password)
        return cls._instance
    
    def _connect(self, host, username, password):
        credentials = pika.PlainCredentials(username, password)
        self.connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, credentials=credentials, heartbeat=0)
            )
        
        queues = ["calc_queue", "trans_queue", "encrypt_queue"]
        
        self.channel = self.connection.channel()
        
        for queue_name in queues:
            self.channel.queue_declare(
                queue=queue_name,
                arguments={
                    'x-message-ttl': 60000 # 메시지 TTL 설정 60초(60000MS)
                },
                durable=True
            )
        
        return self.channel
    
    # 메시지 퍼블리싱
    def queue_publish(self, message, queue_name):
        self.channel.basic_publish(
                exchange='',
                routing_key=queue_name,
                body=message,
                properties=pika.BasicProperties(
                    delivery_mode=2, # 메시지 영구 저장
                )    
        )
        
    # 장기 미사용으로 Channel이 Idel 상태로 변환 시, 재 오픈을 위해 만듬
    def open_channel(self):
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue="calc_queue", durable=True)
    
    def close(self):
        if self.channel:
            self.channel.close()
        if self.connection:
            self.connection.close()
        
        
        

