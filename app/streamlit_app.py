# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run_multi
from fpdf import FPDF
import fpdf as fpdf_module
from datetime import datetime

LOGO_SVG = """
<svg width="100%" viewBox="0 0 680 320" role="img" xmlns="http://www.w3.org/2000/svg">
  <title>MedCheck logo</title>
  <desc>MedCheck logo featuring a shield with a medical cross and a checkmark, with the wordmark beside it</desc>
  <path d="M120 48 L200 48 L200 185 Q160 218 120 238 Q80 218 80 185 Z" fill="#1a56db"/>
  <path d="M120 58 L192 58 L192 183 Q160 210 120 228 Q88 210 88 183 Z" fill="#1e40af" opacity="0.35"/>
  <rect x="97" y="118" width="86" height="28" rx="5" fill="white"/>
  <rect x="126" y="89" width="28" height="86" rx="5" fill="white"/>
  <polyline points="148,162 158,176 178,150" fill="none" stroke="#22c55e" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>
  <text x="222" y="168" font-family="sans-serif" font-weight="500" font-size="52" fill="#1a56db">MedCheck</text>
  <text x="224" y="198" font-family="sans-serif" font-weight="400" font-size="17" fill="#6b7280" letter-spacing="0.04em">drug interaction checker</text>
</svg>
"""

FONTS_DIR = os.path.join(os.path.dirname(fpdf_module.__file__), 'fonts')

def results_to_pdf(results: list[dict]) -> bytes:
    pdf = FPDF()
    pdf.add_font('DejaVu', style='',  fname=os.path.join(FONTS_DIR, 'DejaVuSans.ttf'))
    pdf.add_font('DejaVu', style='B', fname=os.path.join(FONTS_DIR, 'DejaVuSansCondensed-Bold.ttf'))
    pdf.add_font('DejaVu', style='I', fname=os.path.join(FONTS_DIR, 'DejaVuSansCondensed-Oblique.ttf'))
    pdf.add_page()

    pdf.set_font('DejaVu', 'B', 16)
    pdf.cell(0, 10, 'MedCheck Interaction Report', ln=True)
    pdf.set_font('DejaVu', '', 9)
    pdf.cell(0, 6, f"Generated {datetime.now().strftime('%B %d, %Y')}", ln=True)
    pdf.ln(6)

    for r in results:
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 8, f"{r['drug_a'].title()} + {r['drug_b'].title()}", ln=True)
        pdf.set_font('DejaVu', '', 10)
        pdf.multi_cell(0, 6, r['output'])
        if r['sources']:
            pdf.set_font('DejaVu', 'I', 8)
            pdf.cell(0, 5, 'Sources: ' + ', '.join(r['sources']), ln=True)
        pdf.ln(4)

    return bytes(pdf.output())

st.markdown(LOGO_SVG, unsafe_allow_html=True)
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