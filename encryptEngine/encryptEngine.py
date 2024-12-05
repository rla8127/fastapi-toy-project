import hashlib

def encrypt(text):
    try:
        result = hashlib.md5(text.encode()).hexdigest()
        print(result)
        return result
    
    except Exception as e:
        print(f"Error: {e}")

