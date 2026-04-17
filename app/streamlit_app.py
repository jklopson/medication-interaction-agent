# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run_multi
from fpdf import FPDF
from datetime import datetime

def results_to_pdf(results: list[dict]) -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'MedCheck Interaction Report', ln=True)
    pdf.set_font('Helvetica', '', 9)  # was 'Helvatica'
    pdf.cell(0, 6, f"Generated {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.ln(6)

    for r in results:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, f"{r['drug_a'].title()} + {r['drug_b'].title()}", ln=True)
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, r['output'])
        if r['sources']:
            pdf.set_font('Helvetica', 'I', 8)
            pdf.cell(0, 5, 'Sources: ' + ', '.join(r['sources']), ln=True)
        pdf.ln(4)

    return bytes(pdf.output())

st.title('MedCheck')
st.write('Enter a list of your medications below. Either write one per line or separated by commas.')

raw_input = st.text_area('Medications', height=150, placeholder='e.g.\nlisinopril\nmetformin\natorvastatin')

if st.button('Check all interactions'):
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

                st.download_button(
                    label='Download as PDF',
                    data=results_to_pdf([r]),
                    file_name=f"{r['drug_a']}_{r['drug_b']}_interaction.pdf",
                    mime='application/pdf',
                    key=f"dl_{r['drug_a']}_{r['drug_b']}"
                )

        if len(results) > 1:
            st.divider()
            st.download_button(
                label='Download full report (all pairs)',
                data=results_to_pdf(results),
                file_name='medcheck_full_report.pdf',
                mime='application/pdf',
                key='dl_full'
            )