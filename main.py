from dotenv import load_dotenv
from googletrans import Translator
load_dotenv()
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# 간단한 번역 함수
def translate_to_english(text):
    translations = {'호텔': 'hotel', '레저': 'leisure', '펜션': 'pension', '모텔': 'motel', 
                    '사진': 'photo', '일러스트': 'illustration', '3D': '3D', '아이콘': 'icon',
                    '새벽': 'dawn', '오전': 'morning', '오후': 'afternoon', '해질녘': 'dusk', '밤': 'night'}
    return translations.get(text, text)

# 문장을 영어로 번역하는 함수
def translate_sentence_to_english(text):
    translator = Translator()
    translated = translator.translate(text, src='ko', dest='en')
    return translated.text

# 각 이미지 타입에 대한 설명을 반환하는 함수
def get_image_type_description(image_type):
    descriptions = {
        '사진': 'high quality, realistic photo::2',
        '일러스트': 'high quality, illustration::2',
        '3D': '3D rendered',
        '아이콘': 'flat icon'
    }
    return descriptions.get(image_type, 'image')

# StreamHandler 클래스 정의
class StreamHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token.replace('\n', ' ').replace('1.', '').replace('2.', '').replace('Scene 1:', '').replace('In the first scene,', '')  # 줄바꿈, 번호, 'Scene 1:' 제거


# 번역과 프롬프트 생성
def get_prompt(category, image_type, time_of_day, description, image_ratio):
    category_en = translate_to_english(category)
    image_type_en = translate_to_english(image_type)
    time_of_day_en = translate_to_english(time_of_day)
    description_en = translate_sentence_to_english(description)  # 문장 번역
    image_type_description = get_image_type_description(image_type)

    prompt = f"In a {image_type_description} scene during the {time_of_day_en} in a {category_en}, encapsulate the concept of {description_en}."
    fixed_part = f" Photo taken by Richard Avedon with Nikon Z6 and an 85mm lens, Award Winning Photography style, Cinematic and Volumetric Lighting, 8K, Ultra-HD, Super-Resolution --ar {image_ratio} --v 5.2"

    # ChatOpenAI 초기화
    stream_handler = StreamHandler()
    chat_model = ChatOpenAI(streaming=True, callbacks=[stream_handler])

    # 결과 얻기
    chat_model.predict(prompt, max_tokens=100)

    return f"{stream_handler.text} {fixed_part}"

st.title('YANOLJA Midjourney Prompt Generator')

# 사용자 입력 레이아웃
col1, col2, col3, col4 = st.columns(4)
with col1:
    category = st.selectbox('Category', ['호텔', '레저', '펜션', '모텔'])
with col2:
    image_type = st.selectbox('Style', ['사진', '일러스트', '3D', '아이콘'])
with col3:
    time_of_day = st.selectbox('Time', ['새벽', '오전', '오후', '해질녘', '밤'])
with col4:
    image_ratio = st.selectbox('Ratio', ['1:1', '9:16', '16:9', '3:4'])
    
description = st.text_input('원하는 이미지를 묘사해주세요.')

if st.button('프롬프트 생성하기'):
    with st.spinner('프롬프트 생성 중...'):
        final_output = get_prompt(category, image_type, time_of_day, description, image_ratio)
        st.write(final_output)  # final_output만 출력
