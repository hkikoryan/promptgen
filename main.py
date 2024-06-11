

from dotenv import load_dotenv
load_dotenv()
import os
import re
from deep_translator import GoogleTranslator
import streamlit as st
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import requests

st.set_page_config(
    page_title="Prompt Generator",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

openai_api_key = os.getenv("OPENAI_API_KEY")
clipdrop_api_key = os.getenv("CLIPDROP_API_KEY")

# 배경색 설정을 위한 CSS 추가
st.markdown("""
    <style>
     Header {visibility: hidden;}
     footer {visibility: hidden;}


    .stApp {
        background-color: #0e1117;
    }
    .stButton>button {
        border: 2px solid #FD4B48;
        border-radius: 10px;
        color: #ffffff;
        background-color: #FD4B48;
    }
    .stButton>button:hover {
        border: 2px solid #FD4B48;
        color: #FD4B48;
        background-color: transparent;
    }
            
    input::placeholder {
        font-size: 14px; /* 폰트 크기 조절 */
        color: #999999; /* 폰트 색상 조절 */
        opacity: 0.5; /* 플레이스홀더 텍스트의 투명도 조절 */
    }
    input {
        font-size: 14px; /* 입력 텍스트의 폰트 크기 조절 */
    }
    .tooltip {
        display: inline-block;
        position: relative;
        cursor: pointer;
    }
    .tooltip .tooltiptext {
        visibility: hidden;
        width: 200px;
        background-color: black;
        color: white;
        text-align: left;
        border-radius: 6px;
        padding: 5px;
        position: absolute;
        z-index: 1;
        left: 110%;
        margin-left: 5px;
        font-size: 14px
    }
    .tooltip:hover .tooltiptext {
        visibility: visible;
    }
    </style>
    """, unsafe_allow_html=True)



# 간단한 번역 함수
def translate_to_english(text):
    translations = {
        '중간 거리': 'Medium Shot,', '와이드 샷': 'Wide Shot, Full shot,',
        '항공뷰': 'Top view, High Angle shot,', '상반신': 'Upper body shot, Portrait,',
        '클로즈업': 'Close-Up shot,', '호텔': 'luxury hotel,', '레저': 'leisure,', '펜션': 'pension,',
        '모텔': 'motel,', '항공': 'airplane,', '사진': 'photo,', '일러스트': 'illustration,',
        '3D': '3D rendering,', '아이콘': 'flat icon,', '새벽': 'dawn,', '일출': 'Sunrise,', '오전': 'morning,',
        '정오': 'Noonday,', '오후': 'afternoon,', '해질녘': 'dusk,', '밤': 'night,', '봄': 'spring,',
        '여름': 'summer,', '가을': 'autumn,', '겨울': 'winter,', '맑음': 'sunny,', '비': 'rainy,',
        '눈': 'snowy,', '흐림': 'cloudy,', '사람': 'korean, happy expressions, dynamic posture, live photo, real person,',
        '동물': 'animal,', '캐릭터': 'character,', '장소': 'location,', '객체': 'object,',
        '정면': 'front view,', '측면': 'side view, looking at side', '후면': 'back view, looking at behind,'
    }
    return translations.get(text, text)

# 각 이미지 타입에 대한 설명을 반환하는 함수
def get_image_type_description(style):
    descriptions = {
        '사진': 'hyper realistic,', '일러스트': 'Illustration,', '3D': '3D rendered,',
        '아이콘': 'Flat icon, white background,'
    }
    return descriptions.get(style, 'image')

# 문장을 영어로 번역하는 함수
def translate_sentence_to_english(text):
    translator = GoogleTranslator(source='ko', target='en')
    translated = translator.translate(text)
    return translated

# 프롬프트 생성 및 저장
def create_and_store_prompt(style, season, time_of_day, weather, subject, image_ratio, description, composition, camera_view, camera, FaceModel):
    # 프롬프트 생성
    final_output = get_prompt(style, season, time_of_day, weather, subject, image_ratio, description, composition, camera_view, camera, FaceModel)
    # 프롬프트 리스트에 저장
    st.session_state['prompts'].insert(0, final_output)

# 프롬프트 생성 버튼 이벤트 처리
def handle_create_prompt():
    with st.spinner('프롬프트 생성 중...'):
        create_and_store_prompt(
            style, season, time_of_day, weather, subject, image_ratio, description,
            composition if include_composition else None,
            camera_view if include_camera_view else None,
            camera if include_camera else None,
            FaceModel if include_FaceModel else None
        )

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
    headers = {'x-api-key': clipdrop_api_key}
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
        token = re.sub(r'Title:.*?Description:', '', token)
        token = re.sub(r'Scene \d+:', '', token)
        clean_token = token.replace('\n', ' ').replace('1.', '').replace('2.', '')
        self.text += clean_token

def get_prompt(style, season, time_of_day, weather, subject, image_ratio, description, composition=None, camera_view=None, camera=None, FaceModel=None):
     # 번역
    season_en = translate_to_english(season)
    time_of_day_en = translate_to_english(time_of_day)
    weather_en = translate_to_english(weather)
    subject_en = translate_to_english(subject)
    description_en = translate_sentence_to_english(description)
    style_description = get_image_type_description(style)

    # 옵셔널 매개변수 번역 및 설정
    composition_en = translate_to_english(composition) if composition else ""
    camera_view_en = translate_to_english(camera_view) if camera_view else ""

    # FaceModel에 따른 텍스트 추가
    face_model_text = ""
    if FaceModel == '아라':
        face_model_text = "a beautiful woman,"
    elif FaceModel == '국인':
        face_model_text = "a handsome man,"

    # 프롬프트 구성
    prompt_elements = [
        composition_en if composition_en else "", 
        camera_view_en if camera_view_en else "", 
        style_description, 
        season_en, 
        time_of_day_en, 
        weather_en, 
        subject_en, 
        f"{description_en},"  # Description 뒤에 쉼표 추가
    ]
    
    # 고정된 파트가 필요한 경우 설정
    if style == '사진' and camera:
        camera_info = camera  # 고급 설정에서 선택한 카메라 사용
    else:
        camera_info = "Nikon Z7 and a 50mm prime lens"

    fixed_parts = {
        '사진': f"{camera_info}, --style raw --v 6.0",
        '일러스트': "Superflat style, low resolution --niji 6",
        '3D': "3D rendered graphic style",
        '아이콘': "Flat icon style, simple design"
    }
    
    # FaceModel 설정에 따라 추가 요소 삽입
    face_model_part = ""
    if FaceModel == '아라':
        face_model_part = "--cref https://s.mj.run/USpeH9WeCx8 --cw 0"
    elif FaceModel == '국인':
        face_model_part = "--cref https://s.mj.run/PCbQjomU9q8 --cw 0"

    fixed_part = fixed_parts.get(style, "") + (f" --ar {image_ratio}" if image_ratio else "")
    
    # 요소들을 연결하여 최종 프롬프트 생성
    final_prompt = f"{face_model_text} " + " ".join(filter(None, prompt_elements)) + " " + fixed_part + " " + face_model_part
    return final_prompt


# Streamlit 앱 시작
st.title('Prompt Generator')

# 세션 상태에 프롬프트 리스트 초기화
if 'prompts' not in st.session_state:
    st.session_state['prompts'] = []

# 탭을 추가
tab = st.selectbox("Choose a tab", ["Prompter (Midjourney)", "Image Generator", "Upscaler"])

if tab == "Prompter (Midjourney)":
    # 일반 설정
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        style = st.selectbox('Style', ['사진', '일러스트', '아이콘', '3D'])
    with col2:
        season = st.selectbox('Season', ['봄', '여름', '가을', '겨울'])
    with col3:
        time_of_day = st.selectbox('Time', ['새벽', '일출', '오전', '정오', '오후', '해질녘', '밤'])
    with col4:
        weather = st.selectbox('Weather', ['맑음', '비', '눈', '흐림'])
    with col5:
        subject = st.selectbox('Subject', ['사람', '동물', '캐릭터', '장소', '객체'])
    with col6:
        image_ratio = st.selectbox('Ratio', ['1:1', '9:16', '16:9', '3:4', '3:1'])

    # 고급 설정
    with st.expander("Advanced Settings"):
        col7, col8, col9, col10 = st.columns(4)
        with col7:
            include_composition = st.checkbox("Composition")
            if include_composition:
                composition = st.selectbox('Composition', ['중간 거리', '와이드 샷', '항공뷰', '상반신', '클로즈업'])
        with col8:
            include_camera_view = st.checkbox("Camera View")
            if include_camera_view:
                camera_view = st.selectbox('Camera View', ['정면', '측면', '후면'])
        with col9:
            camera_checkbox, camera_tooltip = st.columns([0.8, 0.2])
            with camera_checkbox:
                include_camera = st.checkbox("Camera")
            with camera_tooltip:
                st.markdown("""
                <div class="tooltip">💡
                    <span class="tooltiptext">Canon EOS R5 : 건물 <br> Sony a7R IV : 풍경</span>
                </div>
                """, unsafe_allow_html=True)
            if include_camera:
                camera = st.selectbox('Camera', ['Canon EOS R5 with a 200mm lens', 'Sony a7R IV and a 70mm lens'])
        with col10:
            face_model_checkbox, face_model_tooltip = st.columns([0.8, 0.2])
            with face_model_checkbox:
                include_FaceModel = st.checkbox("FaceModel")
            with face_model_tooltip:
                st.markdown("""
                <div class="tooltip">💡
                    <span class="tooltiptext">아라 : 야놀자 모델<br>국인 : 구긴</span>
                </div>
                """, unsafe_allow_html=True)
            if include_FaceModel:
               FaceModel = st.selectbox('', ['아라', '국인'], key='FaceModel')


    description = st.text_input('Description', placeholder='원하는 이미지를 묘사해주세요.')

    if st.button('프롬프트 생성하기'):
        handle_create_prompt()

    # 현재와 이전 프롬프트들을 항상 표시
    st.markdown(""" <span style='color: #777777;'>Paste the generated prompt into</span> <span style='color: #FD4B48;'>MidJourney</span>
""", unsafe_allow_html=True)
    for idx, prompt in enumerate(st.session_state['prompts']):
        st.text_area(f"Prompt {idx+1}", value=prompt, height=150, key=f"Prompt{idx}")
        





elif tab == "Image Generator":
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        composition = st.selectbox('Composition', ['중간 거리', '와이드 샷', '항공뷰', '상반신', '클로즈업'])
    with col2:
        image_type = st.selectbox('Style', ['사진', '일러스트', '3D', '아이콘'])
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
            api_key = os.getenv('OPENAI_API_KEY')
            image_url = generate_image_with_dalle(api_key, prompt, quality, style)
            if image_url:
                st.write(f"{prompt}")
                st.image(image_url, caption='Generated Image')
            else:
                st.write('Failed to generate image.')

elif tab == "Upscaler":
    uploaded_image = st.file_uploader("Upload an image", type=["jpg", "jpeg", "png"])
    if uploaded_image is not None:
        original_image = Image.open(uploaded_image)
        original_width, original_height = original_image.size
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)
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
