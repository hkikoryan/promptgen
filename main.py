from dotenv import load_dotenv
load_dotenv()
import streamlit as st
from langchain.chat_models import ChatOpenAI
from langchain.callbacks.base import BaseCallbackHandler

# StreamHandler 클래스 정의
class StreamHandler(BaseCallbackHandler):
    def __init__(self, container, initial_text=""):
        self.container = container
        self.text = initial_text
    def on_llm_new_token(self, token: str, **kwargs) -> None:
        self.text += token
        self.container.markdown(self.text)

st.title('AI Copy Writer')
st.title('당신을 위한 광고 문구를 생성해드립니다.')

content1 = st.text_input('브랜드 명을 적어주세요.')
content2 = st.text_input('원하는 광고 문구를 적어주세요.')

# stream_handler 객체 생성
chat_box = st.empty()
stream_handler = StreamHandler(chat_box)

# 이제 ChatOpenAI 초기화
chat_model = ChatOpenAI(streaming=True, callbacks=[stream_handler])

if st.button('광고 문구 요청하기'):
    with st.spinner('광고 문구 작성중..'):
        result = chat_model.predict(content1 + "에 대한 브랜드의 핵심 내용을 짧게 정리하고" + content2 + "에 관련된 짧고 매력있는 광고 카피를 이모티콘을 포함해서 5가지를 만들어줘")
