# from dotenv import load_dotenv
# load_dotenv()
import streamlit as st
from langchain.chat_models import ChatOpenAI

chat_model = ChatOpenAI()

st.title('AI Copy Writer')
st.title('AI가 당신을 위한 :blue[광고 문구]를 생성해드립니다. :sunglasses:')

content = st.text_input('원하는 광고 문구를 적어주세요.')

if st.button('광고 문구 요청하기'):
    with st.spinner('광고 문구 작성중..'):
        result = chat_model.predict(content + "에 대한 짧고 매력있는 광고 문구 5가지를 만들어줘")
        st.write(result)



