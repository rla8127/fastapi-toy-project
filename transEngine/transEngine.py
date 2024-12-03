from googletrans import Translator

# Translator 객체 생성
translator = Translator()

def translate(text, direction):
    try:
        if direction == 1:
            translated = translator.translate(text, src='ko', dest='en').text
        else:  # 'en_to_ko'
            translated = translator.translate(text, src='en', dest='ko').text

        return translated
    
    except Exception as e:
        print(f"Error: {e}")
        
    
