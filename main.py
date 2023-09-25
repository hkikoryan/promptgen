# from dotenv import load_dotenv
# load_dotenv()
import streamlit as st
from langchain.chat_models import ChatOpenAI
chat_model = ChatOpenAI()

st.title('인공지능 시인')
st.title('_AI가 대신_ :blue[시를] 지어드립니다. :sunglasses:')

content = st.text_input('시의 주제를 적어주세요.')

if st.button('시 작성 요청하기'):
    with st.spinner('시 작성중..'):
        result = chat_model.predict(content + "에 대한 시를 써줘")
        st.write(result)


