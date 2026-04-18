# app/streamlit_app.py
import streamlit as st
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from agent.react_loop import run_multi
import base64
from datetime import datetime

from fpdf import FPDF

GIF_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'Bird_Doctor_GIF.gif')

def sanitize(text: str) -> str:
    return (text
        .replace('\u2014', '--')
        .replace('\u2013', '-')
        .replace('\u2018', "'")
        .replace('\u2019', "'")
        .replace('\u201c', '"')
        .replace('\u201d', '"')
        .replace('\u2026', '...')
        .encode('ascii', errors='ignore').decode('ascii')
    )

def results_to_pdf(results: list[dict]) -> bytes:
    pdf = FPDF()
    pdf.add_page()

    pdf.set_font('Helvetica', 'B', 16)
    pdf.cell(0, 10, 'MedCheck Interaction Report', new_x="LMARGIN", new_y="NEXT")
    pdf.set_font('Helvetica', '', 9)
    pdf.cell(0, 6, f"Generated {datetime.now().strftime('%B %d, %Y')}", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    for r in results:
        pdf.set_font('Helvetica', 'B', 12)
        pdf.cell(0, 8, f"{r['drug_a'].title()} + {r['drug_b'].title()}", new_x="LMARGIN", new_y="NEXT")
        pdf.set_font('Helvetica', '', 10)
        pdf.multi_cell(0, 6, sanitize(r['output']))
        if r['sources']:
            pdf.set_font('Helvetica', 'I', 8)
            pdf.multi_cell(190, 5, 'Sources: ' + sanitize(', '.join(r['sources'])))
        pdf.ln(4)

    return bytes(pdf.output())

st.markdown("""
    <div style='display:flex; justify-content:center;'>
      <svg width="540" viewBox="0 0 680 260" role="img" xmlns="http://www.w3.org/2000/svg">
        <g transform="translate(80, 40)">
          <path d="M60 0 L120 0 Q134 0 134 14 L134 80 Q134 128 90 148 Q46 128 46 80 L46 14 Q46 0 60 0 Z" fill="#2563EB"/>
          <rect x="81" y="46" width="18" height="56" rx="3" fill="#ffffff"/>
          <rect x="62" y="65" width="56" height="18" rx="3" fill="#ffffff"/>
          <circle cx="120" cy="132" r="18" fill="#10B981"/>
          <polyline points="111,132 118,139 130,124" fill="none" stroke="#ffffff" stroke-width="4" stroke-linecap="round" stroke-linejoin="round"/>
          <text x="158" y="90" font-family="sans-serif" font-size="58" font-weight="500">
            <tspan fill="#2563EB">Med</tspan><tspan fill="#1e293b">Check</tspan>
          </text>
          <text x="160" y="118" font-family="sans-serif" font-size="16" font-weight="400" fill="#9ca3af">DRUG INTERACTION CHECKER</text>
          <line x1="160" y1="130" x2="460" y2="130" stroke="#2563EB" stroke-width="1.5" opacity="0.3"/>
        </g>
      </svg>
    </div>
    <p style='text-align:center; color:#6b7280; margin-top:1rem;'>Enter your medications below, one per line. MedCheck will check for known interactions which can be downloaded as a PDF! Please consult a medical professional before taking any actions based on our analysis.</p>
    <br/>
""", unsafe_allow_html=True)

raw_input = st.text_area('Medications', height=150, placeholder='e.g.\nlisinopril\nmetformin\natorvastatin')

if st.button('Check all interactions'):
    drugs = [d.strip() for d in raw_input.replace(',', '\n').splitlines() if d.strip()]

    if len(drugs) < 2:
        st.warning('Please enter at least two medications.')
    else:
        st.info(f'Checking {len(list(__import__("itertools").combinations(drugs, 2)))} pairs...')

        with open(GIF_PATH, 'rb') as f:
            gif_b64 = base64.b64encode(f.read()).decode()

        loading_slot = st.empty()
        loading_slot.markdown(f"""
            <div style="text-align:center; padding: 1rem 0;">
                <img src="data:image/gif;base64,{gif_b64}" width="220"/>
                <div style="margin-top:14px;">
                    <span style="font-size:22px; font-weight:500; color:#1a56db;">
                        Analyzing Medical Data<span class="dots"></span>
                    </span>
                </div>
            </div>
            <style>
            .dots::after {{
                content: '';
                animation: dotcycle 1.5s steps(1, end) infinite;
            }}
            @keyframes dotcycle {{
                0%   {{ content: ''; }}
                25%  {{ content: '.'; }}
                50%  {{ content: '..'; }}
                75%  {{ content: '...'; }}
                100% {{ content: ''; }}
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