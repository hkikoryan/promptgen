from dotenv import load_dotenv
load_dotenv()
import os
import streamlit as st
from PIL import Image
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler
import requests  # Clipdrop API와 DALL-E API 호출을 위해 필요

openai_api_key = os.getenv("OPENAI_API_KEY")
clipdrop_api_key = os.getenv("CLIPDROP_API_KEY")

# 간단한 번역 함수
def translate_to_english(text):
    translations = {
        '호텔': 'hotel', '레저': 'leisure', '펜션': 'pension', '모텔': 'motel',
        '사진': 'photo', '일러스트': 'illustration', '3D': '3D', '아이콘': 'icon',
        '새벽': 'dawn', '오전': 'morning', '오후': 'afternoon', '해질녘': 'dusk', '밤': 'night',
        '봄': 'spring', '여름': 'summer', '가을': 'autumn', '겨울': 'winter'  # 계절 번역 추가
    }
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

# DALL-E 3 API를 호출하여 이미지 생성
def generate_image_with_dalle(api_key, prompt):
    url = "https://api.openai.com/v1/images/generations"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }
    data = {
        "prompt": prompt,
        "n": 1  # 생성할 이미지의 수
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
    headers = {'x-api-key': "CLIPDROP_API_KEY"}
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
        clean_token = token.replace('\n', ' ').replace('1.', '').replace('2.', '').replace('Scene 1:', '')  # 줄바꿈, 번호, 'Scene 1:' 제거
        self.text += clean_token


# 번역과 프롬프트 생성
def get_prompt(category, image_type, season, time_of_day, description, image_ratio=None, include_fixed_part=True):
    # ChatOpenAI 초기화 (함수 시작 부분으로 이동)
    stream_handler = StreamHandler()
    chat_model = ChatOpenAI(streaming=True, callbacks=[stream_handler])
    season_en = translate_to_english(season)  # 계절 번역
    category_en = '' if category == '없음' else translate_to_english(category)
    image_type_en = translate_to_english(image_type)
    time_of_day_en = translate_to_english(time_of_day)
    description_en = translate_sentence_to_english(description)  # 문장 번역
    image_type_description = get_image_type_description(image_type)
    category_phrase = f"in a {category_en}," if category_en else ""
    
    prompt = f"In a {image_type_description} scene during {season_en}, {time_of_day_en} {category_phrase} encapsulate the concept of {description_en}."
    
    # image_type에 따른 fixed_part 설정 및 max_tokens 설정
    max_tokens = 50  # 기본값
    if image_type == '사진':
        fixed_part = f"Photo taken by Richard Avedon with Nikon Z6 and an 85mm lens, Award Winning Photography style, Cinematic and Volumetric Lighting, 8K, Ultra-HD, Super-Resolution --ar {image_ratio}"
    elif image_type == '일러스트':
        fixed_part = f"in the style of superflat style, light {time_of_day_en}, cinestill 50d, editorial illustrations::2, sleepycore, subtle tonal values, low resolution  --ar {image_ratio}"
    elif image_type == '3D':
        fixed_part = f"in the style of 3d::2 graphic --ar {image_ratio}"
    elif image_type == '아이콘':
        fixed_part = f"in the style of simple icon::2 --ar {image_ratio}"
        max_tokens = 20  # 아이콘의 경우에는 더욱 짧게

    # 최종 프롬프트 생성
    if include_fixed_part:
        final_prompt = f"{prompt} {fixed_part}"
    else:
        final_prompt = prompt
    
    # 결과 얻기
    chat_model.predict(prompt, max_tokens=max_tokens)
    return f"{stream_handler.text} {fixed_part if include_fixed_part else ''}"


# Streamlit 앱 시작
st.title('YAD (Yanolja AI Designer)')

# 탭을 추가
tab = st.selectbox("Choose a tab", ["Prompter", "Image Generator", "Upscaler"])


if tab == "Prompter":
    # 사용자 입력 레이아웃
    col1, col2, col3, col4, col5 = st.columns(5)  # 컬럼 5개로 변경
    with col1:
        category = st.selectbox('Category', ['없음', '호텔', '펜션', '레저', '모텔'])
    with col2:
        image_type = st.selectbox('Style', ['사진', '일러스트', '3D', '아이콘'])
    with col3:
        season = st.selectbox('Season', ['봄', '여름', '가을', '겨울'])  # 계절 선택 상자 추가
    with col4:
        time_of_day = st.selectbox('Time', ['새벽', '오전', '오후', '해질녘', '밤'])  # 기존의 컬럼 3에서 컬럼 4로 이동
    with col5:
        image_ratio = st.selectbox('Ratio', ['1:1', '9:16', '16:9', '3:4'])  # 기존의 컬럼 4에서 컬럼 5로 이동
        
    description = st.text_input('원하는 이미지를 묘사해주세요.')

    if st.button('프롬프트 생성하기'):
        with st.spinner('프롬프트 생성 중...'):
            # get_prompt 함수 호출 시 season도 인수로 전달
            final_output = get_prompt(category, image_type, season, time_of_day, description, image_ratio)
            st.write(final_output)  # final_output만 출력



elif tab == "Image Generator":
    # 사용자 입력 레이아웃
    col1, col2, col3,col4 = st.columns(4)
    with col1:
        category = st.selectbox('Category', ['호텔', '레저', '펜션', '모텔'])
    with col2:
        image_type = st.selectbox('Style', ['사진', '일러스트', '3D', '아이콘'])
    with col3:
        season = st.selectbox('Season', ['봄', '여름', '가을', '겨울'])  # 계절 선택 상자 추가
    with col4:
        time_of_day = st.selectbox('Time', ['새벽', '오전', '오후', '해질녘', '밤'])
    description = st.text_input('원하는 이미지를 묘사해주세요.')
    if st.button('이미지 생성하기'):
        with st.spinner('이미지 생성 중...'):
            prompt = get_prompt(category, image_type, season , time_of_day, description, include_fixed_part=False)
            api_key = os.getenv('OPENAI_API_KEY')  # .env 파일에서 API 키 가져오기
            image_url = generate_image_with_dalle(api_key, prompt)

            if image_url:
                st.write(f"{prompt}")  # 도출된 프롬프트 출력
                st.image(image_url, caption='Generated Image')  # 생성된 이미지 출력
            else:
                st.write('이미지 생성 실패')


# 나머지 코드는 동일합니다.

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
            target_width = st.number_input("Target Width", min_value=1, max_value=4096, value=1024)
            target_height = st.number_input("Target Height", min_value=1, max_value=4096, value=1024)
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
                st.error("이미지 업스케일링에 실패했습니다.")
