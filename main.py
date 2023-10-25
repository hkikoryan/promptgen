#from dotenv import load_dotenv
#load_dotenv()

import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# 간단한 번역 함수
def translate_to_english(text):
    translations = {'호텔': 'hotel', '레저': 'leisure', '펜션': 'pension', '모텔': 'motel', '사진': 'photo', '일러스트': 'illustration', '3D': '3D'}
    return translations.get(text, text)

# StreamHandler 클래스 정의
class StreamHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token

# 번역
def get_prompt(category, image_type, description, image_ratio):
    category_en = translate_to_english(category)
    image_type_en = translate_to_english(image_type)

    prompt = f"Imagine a scene in a {category_en} related to {image_type_en} that encapsulates the concept of {description}."
    fixed_part = f"Photo taken by Sooyeon Lee with Nikon Z6 and an 85mm lens, Award Winning Photography style, Cinematic and Volumetric Lighting, 8K, Ultra-HD, Super-Resolution --ar {image_ratio} --v 5.2"
    
    # ChatOpenAI 초기화
    stream_handler = StreamHandler()
    chat_model = ChatOpenAI(streaming=True, callbacks=[stream_handler])

    # 100자로 제한하여 결과를 얻음
    chat_model.predict(prompt, max_tokens=100)
    
    return f"/imagine prompt: {stream_handler.text} {fixed_part}"

st.title('Midjourney Prompt Generator')

# 사용자 입력
category = st.selectbox('원하는 카테고리를 선택해주세요.', ['호텔', '레저', '펜션', '모텔'])
image_type = st.selectbox('원하는 이미지의 형태를 선택해주세요.', ['사진', '일러스트', '3D'])
description = st.text_input('원하는 이미지를 묘사해주세요.')
image_ratio = st.selectbox('원하는 이미지의 비율을 선택해주세요.', ['1:1', '9:16', '16:9', '3:4'])

if st.button('프롬프트 생성하기'):
    with st.spinner('프롬프트 생성 중...'):
        final_output = get_prompt(category, image_type, description, image_ratio)
        st.write(final_output)  # final_output만 출력
