# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run

st.title('MedCheck')

drug_a = st.text_input('First medication')
drug_b = st.text_input('Second medication')

if st.button('Generate report'):
    with st.spinner('Checking...'):
        result = run(drug_a.strip(), drug_b.strip())
    st.write(result['output'])
