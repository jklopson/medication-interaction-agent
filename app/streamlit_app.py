# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run_multi

st.title('MedCheck')
st.write('Enter a list of your medications below. Either write one per line or separated by commas.')


raw_input = st.text_area('Medications', height=150, placeholder='e.g.\nlisinopril\nmetformin\natorvastatin')

drug_a = st.text_input('First medication')
drug_b = st.text_input('Second medication')

#if st.button('Generate report'):
  #  with st.spinner('Checking...'):
   #     result = run(drug_a.strip(), drug_b.strip())
   # st.write(result['output'])

if st.button('Check all interactions'):
    # Parse: split on newlines or commas, strip, drop blanks
    drugs = [d.strip() for d in raw_input.replace(',', '\n').splitlines() if d.strip()]

    if len(drugs) < 2:
        st.warning('Please enter at least two medications.')
    else:
        st.info(f'Checking {len(list(__import__("itertools").combinations(drugs, 2)))} pairs...')
        results = run_multi(drugs)

        for r in results:
            label = f"{r['drug_a'].title()} + {r['drug_b'].title()}"
            with st.expander(label, expanded=not r['refused']):
                st.write(r['output'])
                if r['sources']:
                    st.caption('Sources: ' + ', '.join(r['sources']))
                elif r['refused']:
                    st.caption('No sufficient FDA data found for this pair.')