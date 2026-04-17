# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run_multi
from fpdf import FPDF
import fpdf as fpdf_module
from datetime import datetime

<<<<<<< HEAD
FONTS_DIR = os.path.dirname(os.path.abspath(__file__))
=======
GIF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Bird_Doctor_GIF.gif')

FONTS_DIR = os.path.join(os.path.dirname(fpdf_module.__file__), 'fonts')
>>>>>>> 0f65469c443dc9b33aa602b355057d049654b0fb

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

st.markdown("<h1 style='text-align:center;'>MedCheck</h1><p style='text-align:center; color:#6b7280;'>Drug Interaction Checker</p>", unsafe_allow_html=True)
st.write('Enter a list of your medications below. Either write one per line or separated by commas.')

raw_input = st.text_area('Medications', height=150, placeholder='e.g.\nlisinopril\nmetformin\natorvastatin')

if st.button('Check all interactions'):
    drugs = [d.strip() for d in raw_input.replace(',', '\n').splitlines() if d.strip()]

    if len(drugs) < 2:
        st.warning('Please enter at least two medications.')
    else:
        st.info(f'Checking {len(list(__import__("itertools").combinations(drugs, 2)))} pairs...')

        import base64
        with open(GIF_PATH, 'rb') as f:
            gif_bytes = f.read()
        gif_b64 = base64.b64encode(gif_bytes).decode()
        loading_slot = st.empty()
        loading_slot.markdown(f"""
            <div style="text-align:center; padding: 1rem 0;">
                <img src="data:image/gif;base64,{gif_b64}" width="220"/>
                <div style="overflow:hidden; white-space:nowrap; margin-top:12px;">
                    <span style="display:inline-block; font-size:22px; font-weight:500;
                                 animation: marquee 3s linear infinite;">
                        Loading &nbsp;&nbsp;&nbsp; Loading &nbsp;&nbsp;&nbsp; Loading &nbsp;&nbsp;&nbsp;
                        Loading &nbsp;&nbsp;&nbsp; Loading &nbsp;&nbsp;&nbsp; Loading &nbsp;&nbsp;&nbsp;
                    </span>
                </div>
            </div>
            <style>
            @keyframes marquee {{
                0%   {{ transform: translateX(100%); }}
                100% {{ transform: translateX(-100%); }}
            }}
            </style>
        """, unsafe_allow_html=True)

        results = run_multi(drugs)
        loading_slot.empty()

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