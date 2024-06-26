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
# from streamlit_auth import login, callback  # Google 로그인 및 인증 관련 코드 숨김




st.set_page_config(
    page_title="Prompt Generator",
    page_icon="🌟",
    layout="wide",
    initial_sidebar_state="expanded"
)

openai_api_key = os.getenv("OPENAI_API_KEY")
clipdrop_api_key = os.getenv("CLIPDROP_API_KEY")

# Google 로그인 및 인증 관련 코드 숨김
# if 'user' not in st.session_state:
#     if 'code' in st.query_params:
#         callback()
#     else:
#         login()
#     st.stop()  # 로그인 후에만 아래 코드가 실행되도록 함
# else:
#     user_info = st.session_state['user']
#     st.write(f"Hello, {user_info['name']} ({user_info['email']})")


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

    
# StreamHandler 클래스 정의    
class StreamHandler(BaseCallbackHandler):
    def __init__(self):
        self.text = ""

    def on_llm_new_token(self, token: str, **kwargs) -> None:
        token = re.sub(r'Title:.*?Description:', '', token)
        token = re.sub(r'Scene \d+:', '', token)
        clean_token = token.replace('\n', ' ').replace('1.', '').replace('2.', '')
        self.text += clean_token

# 프롬프트 생성 함수
def get_prompt(style, season, time_of_day, weather, subject, image_ratio, description, composition=None, camera_view=None, camera=None, FaceModel=None):
    season_en = translate_to_english(season) if season != '선택' else ""
    time_of_day_en = translate_to_english(time_of_day) if time_of_day != '선택' else ""
    weather_en = translate_to_english(weather) if weather != '선택' else ""
    subject_en = translate_to_english(subject) if subject != '선택' else ""
    description_en = translate_sentence_to_english(description)
    style_description = get_image_type_description(style)

    composition_en = translate_to_english(composition) if composition else ""
    camera_view_en = translate_to_english(camera_view) if camera_view else ""

    face_model_text = ""
    if FaceModel == '아라':
        face_model_text = "a beautiful woman,"
    elif FaceModel == '국인':
        face_model_text = "a handsome man,"

    prompt_elements = [
        composition_en, 
        camera_view_en, 
        style_description, 
        season_en, 
        time_of_day_en, 
        weather_en, 
        subject_en, 
        f"{description_en},"
    ]

    prompt_elements = [element for element in prompt_elements if element]

    camera_info = "Nikon Z7 and a 50mm prime lens"
    if style == '사진' and camera:
        camera_info = camera

    fixed_parts = {
        '사진': f"{camera_info}, --style raw --v 6.0",
        '일러스트': "Superflat style, low resolution --niji 6",
        '3D': " white background with a 3D isometric view render in C4D using soft studio lighting at a high resolution and simple design",
        '아이콘': "Flat icon style, simple design"
    }

    face_model_part = ""
    if FaceModel == '아라':
        face_model_part = "--cref https://s.mj.run/USpeH9WeCx8 --cw 0"
    elif FaceModel == '국인':
        face_model_part = "--cref https://s.mj.run/PCbQjomU9q8 --cw 0"

    fixed_part = fixed_parts.get(style, "") + (f" --ar {image_ratio}" if image_ratio else "")

    final_prompt = f"{face_model_text} " + " ".join(filter(None, prompt_elements)) + " " + fixed_part + " " + face_model_part
    return final_prompt

# Streamlit 앱 시작
st.title('Prompt Generator')

# 세션 상태에 프롬프트 리스트 초기화
if 'prompts' not in st.session_state:
    st.session_state['prompts'] = []


# 일반 설정
tab = st.selectbox("Choose a tab", ["Prompter (Midjourney)"])

if tab == "Prompter (Midjourney)":
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    with col1:
        style = st.selectbox('Style', ['사진', '일러스트', '아이콘', '3D'])
    with col2:
        season = st.selectbox('Season', ['선택', '봄', '여름', '가을', '겨울'])
    with col3:
        time_of_day = st.selectbox('Time', ['선택', '새벽', '일출', '오전', '정오', '오후', '해질녘', '밤'])
    with col4:
        weather = st.selectbox('Weather', ['선택', '맑음', '비', '눈', '흐림'])
    with col5:
        subject = st.selectbox('Subject', ['선택', '사람', '동물', '캐릭터', '장소', '객체'])
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
                    <span class="tooltiptext">Canon EOS R5 : 건물 <br> Sony Alpha a7 III  : 풍경</span>
                </div>
                """, unsafe_allow_html=True)
            if include_camera:
                camera = st.selectbox('Camera', ['Canon EOS R5 with a 200mm lens', 'Sony Alpha a7 III'])
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
        



















