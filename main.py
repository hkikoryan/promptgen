from dotenv import load_dotenv
load_dotenv()
import os
import re
from deep_translator import GoogleTranslator  # 수정: deep_translator 추가
import streamlit as st
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import requests  # Clipdrop API와 DALL-E API  

openai_api_key = os.getenv("OPENAI_API_KEY")
clipdrop_api_key = os.getenv("CLIPDROP_API_KEY")


# 배경색 설정을 위한 CSS 추가
st.markdown("""
    <style>
    .stApp {
        background-color: #3B455E;s
    }
     .stButton>button {
        border: 2px solid #F4588C;
        border-radius: 10px;  # 버튼의 모서리를 둥글게
        color: #111111;
        background-color: #F4588C;
    }
    .stButton>button:hover {
        border: 2px solid #F4588C;
        color: #F4588C;
        background-color: transparent;
    }
    </style>
    """, unsafe_allow_html=True)


# 간단한 번역 함수
def translate_to_english(text):
    translations = {
        '중간 거리': 'Medium Shot,', '와이드 샷': 'Wide Shot, Full shot,',
        '항공뷰': 'Top view, High Angle shot,', '상반신': 'Upper body shot, Portrait,',
        '클로즈업': 'Close-Up shot,',
        '호텔': 'hotel,', '레저': 'leisure,', '펜션': 'pension,', '모텔': 'motel,', '항공': 'plane,',
        '사진': 'photo,', '일러스트': 'illustration,', '3D': '3D,', '아이콘': 'icon,',
        '새벽': 'dawn,', '오전': 'mornin,g', '오후': 'afternoon,', '해질녘': 'dusk,', '밤': 'night,',
        '봄': 'spring,', '여름': 'summer,', '가을': 'autumn,', '겨울': 'winter,'
    }
    return translations.get(text, text)


# 문장을 영어로 번역하는 함수
def translate_sentence_to_english(text):
    translator = GoogleTranslator(source='ko', target='en')
    translated = translator.translate(text)
    return translated


# 각 이미지 타입에 대한 설명을 반환하는 함수
def get_image_type_description(image_type):
    descriptions = {
        '사진': 'Cinematic,',
        '일러스트': 'Illustration,',
        '3D': '3D rendered,',
        '아이콘': 'Flat icon, white background'
    }
    return descriptions.get(image_type, 'image')


# DALL-E 3 API를 호출하여 이미지 생성
def generate_image_with_dalle(api_key, prompt, quality='standard', style='vivid'):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": prompt,
        "n": 1,
        "model": "dall-e-3",
        "quality": quality,
        "style": style
    }
    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        image_url = response.json()['data'][0]['url']
        return image_url
    else:
        return None


# Clipdrop API 호출 함수
def call_clipdrop(image_path, target_width, target_height):
    url = "https://clipdrop-api.co/image-upscaling/v1/upscale"
    headers = {'x-api-key': "9114aa67c0fa31e75f7a1d5312172bc807fcc617b4be832c5e22c20f63053370842e202c0a1bc82204c812899639d7f8"}
    files = {'image_file': open(image_path, 'rb')}
    data = {'target_width': target_width, 'target_height': target_height}
    response = requests.post(url, headers=headers, files=files, data=data)
    if response.status_code == 200:
        return response.content
    else:
        st.error(f"Error: {response.json().get('error', 'Unknown error')}")
        return None
    
# StreamHandler 클래스 정의    
class StreamHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        # 불필요한 부분을 제거하는 로직
        token = re.sub(r'Title:.*?Description:', '', token)
        token = re.sub(r'Scene \d+:', '', token)

        # 줄바꿈 및 기타 문자 제거 로직
        clean_token = token.replace('\n', ' ').replace('1.', '').replace('2.', '')
        self.text += clean_token


# 번역과 프롬프트 생성
def get_prompt(composition, image_type, season, time_of_day, description, image_ratio=None, include_fixed_part=True):
    # 번역
    season_en = translate_to_english(season)
    composition_en = translate_to_english(composition) if composition != '없음' else ""
    time_of_day_en = translate_to_english(time_of_day)
    description_en = translate_sentence_to_english(description)

    # 이미지 타입에 따른 설명
    image_type_description = get_image_type_description(image_type)

    # 추가된 문장 구성요소
    detailed_description = f"This image should represent a scene where {description_en} during {time_of_day_en} in {season_en}. It should capture the essence of {composition_en} in a style that reflects {image_type_description}."

    # 프롬프트 구성
    prompt_elements = [image_type_description, season_en, time_of_day_en, composition_en, description_en]
    prompt = f"{' '.join(filter(None, prompt_elements))}"

    # fixed_part 설정
    fixed_parts = {
        '사진': "8K Ultra-HD, Kodak Portra 400, Canon EOS 5D Mark IV --style raw --v 6.0",
        '일러스트': "Superflat style, low resolution",
    
    }
    fixed_part = fixed_parts.get(image_type, "") + (f" --ar {image_ratio}" if image_ratio else "")

    # 최종 프롬프트에 fixed_part 포함
    final_prompt = f"{prompt}. {fixed_part}" if include_fixed_part else prompt
    return final_prompt


# Streamlit 앱 시작
st.title('Image Generator')

# 탭을 추가
tab = st.selectbox("Choose a tab", ["Prompter (Midjourney)"])

if tab == "Prompter (Midjourney)":
    # 사용자 입력 레이아웃
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        composition = st.selectbox('Composition', ['중간 거리', '와이드 샷', '항공뷰', '상반신', '클로즈업'])
    with col2:
        image_type = st.selectbox('Style', ['사진', '일러스트'])
    with col3:
        season = st.selectbox('Season', ['봄', '여름', '가을', '겨울'])
    with col4:
        time_of_day = st.selectbox('Time', ['새벽', '오전', '오후', '해질녘', '밤'])
    with col5:
        image_ratio = st.selectbox('Ratio', ['1:1', '9:16', '16:9', '3:4'])
    description = st.text_input('원하는 이미지를 묘사해주세요.')
    if st.button('프롬프트 생성하기'):
        with st.spinner('프롬프트 생성 중...'):
            final_output = get_prompt(composition, image_type, season, time_of_day, description, image_ratio)
            modified_prompt = st.text_area("생성된 프롬프트:", value=final_output, height=150)
            st.write("생성된 프롬프트를 미드저니에 붙여넣어주세요.")


elif tab == "Image Generator":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        composition = st.selectbox('Composition', ['중간 거리', '와이드 샷', '항공뷰', '상반신', '클로즈업'])
    with col2:
        image_type = st.selectbox('Style', ['사진', '일러스트'])
    with col3:
        season = st.selectbox('Season', ['봄', '여름', '가을', '겨울'])
    with col4:
        time_of_day = st.selectbox('Time', ['새벽', '오전', '오후', '해질녘', '밤'])

    quality = st.selectbox('Quality', ['standard', 'hd'])
    style = st.selectbox('Style', ['vivid', 'natural'])
    description = st.text_input('Describe the image you want.')
    
    if st.button('Generate Image'):
        with st.spinner('Generating image...'):
            prompt = get_prompt(composition, image_type, season, time_of_day, description, include_fixed_part=False)
            api_key = os.getenv('OPENAI_API_KEY')  # .env 파일에서 API 키 가져오기
            image_url = generate_image_with_dalle(api_key, prompt, quality, style)
            if image_url:
                st.write(f"{prompt}")  # 도출된 프롬프트 출력
                st.image(image_url, caption='Generated Image')  # 생성된 이미지 출력
            else:
                st.write('Failed to generate image.')
            

elif tab == "Upscaler":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        # 원본 이미지 크기 확인
        original_image = Image.open(uploaded_image)
        original_width, original_height = original_image.size
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
        # 타겟 크기 설정 옵션
        size_option = st.selectbox("Choose the scale factor or input size", ['Custom', '2x', '3x', '4x'])
        if size_option == 'Custom':
            target_width = st.number_input("Target Width", min_value=1, max_value=4096, value=original_width)
            target_height = st.number_input("Target Height", min_value=1, max_value=4096, value=original_height)
        else:
            scale_factor = int(size_option.replace('x', ''))
            target_width = original_width * scale_factor
            target_height = original_height * scale_factor
        if st.button("Upscale Image"):
            image_path = "/tmp/uploaded_image_to_upscale.jpg"
            with open(image_path, "wb") as f:
                f.write(uploaded_image.getbuffer())
            upscale_image_bytes = call_clipdrop(image_path, target_width, target_height)
            if upscale_image_bytes is not None:
                st.download_button(
                    "Download Upscaled Image",
                    upscale_image_bytes,
                    file_name="upscaled_image.jpg",
                    mime="image/jpeg"
                )
            else:
                st.error("Failed to upscale the image.")