import streamlit as st
import json

dic = dict(st.secrets['credentials'])
user_encode_data = json.dumps(dic, indent=2).encode('utf-8')

st.write(user_encode_data)