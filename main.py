# from dotenv import load_dotenv
# load_dotenv()
import streamlit as st
from langchain.chat_models import ChatOpenAI

chat_model = ChatOpenAI()

st.title('광고문구 AI')
st.title('_AI가 대신_ :blue[광고문구]를 생성해드립니다. :sunglasses:')

content = st.text_input('원하는 광고 문구를 적어주세요.')

if st.button('광고 문구 요청하기'):
    with st.spinner('광고 문구 작성중..'):
        result = chat_model.predict(content + "에 대한 짧은 광고 문구 5가지를 만들어줘")
        st.write(result)



