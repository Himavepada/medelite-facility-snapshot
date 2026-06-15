# app.py
import streamlit as st
import io
import os
from facility_data import get_cms_facility_data

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def create_pdf_report(facility_info, manual_data):
    buffer = io.BytesIO()
    # Margins optimized slightly to maximize clean single-page delivery
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=25, bottomMargin=25)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('TitleStyle', parent=styles['Heading1'], fontSize=15, leading=20, alignment=1, textColor=colors.HexColor("#000000"))
    subtitle_style = ParagraphStyle('SubTitleStyle', parent=styles['Heading2'], fontSize=11, leading=15, alignment=1, textColor=colors.HexColor("#000000"))
    body_style = styles['Normal']
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontName='Helvetica-Bold')
    
    # 1.  BRANDING HEADER (Pulls your exact logo.png smoothly)
    if os.path.exists("logo.png"):
        # Explicitly sizing to your exact 70x71 file bounds to keep it crisp
        logo = RLImage("logo.png", width=70, height=71)
        logo.hAlign = 'CENTER'
        story.append(logo)
        story.append(Spacer(1, 4))
    else:
        # Seamless text backup if image file paths switch environments
        story.append(Paragraph("<b>INFINITE</b>", title_style))
        story.append(Paragraph("<font size=10 color='#4A5568'>Managed by MEDELITE</font>", title_style))
        story.append(Spacer(1, 5))
        
    story.append(Paragraph("<b>FACILITY ASSESSMENT SNAPSHOT</b>", subtitle_style))
    story.append(Paragraph(f"<b>{facility_info.get('state_code', 'US')}</b>", subtitle_style))
    story.append(Spacer(1, 8))
    
    final_name = manual_data['override_name'] if manual_data['override_name'] else facility_info['legal_name']
    
    # Expanded Table List matching your reference layout fields
    report_data = [
        [Paragraph("<b>Report Field Name</b>", bold_style), Paragraph("<b>Value / Information</b>", bold_style)],
        ["Name of Facility", final_name],
        ["Location", facility_info['location']],
        ["EMR", manual_data['emr']],
        ["Census Capacity", facility_info['certified_beds']],
        ["Current Census", manual_data['current_census']],
        ["Type of Patient", manual_data['patient_type']],
        ["Previous Coverage from Medelite", manual_data['medelite_history']],
        ["Previous Provider Performance from Medelite", manual_data['medelite_perf']],
        ["Medical Coverage", manual_data['medical_coverage']],
        ["Overall Star Rating", facility_info['overall_rating']],
        ["Health Inspection", facility_info['health_inspection_rating']],
        ["Staffing", facility_info['staffing_rating']],
        ["Quality of Resident Care", facility_info['quality_delivery_rating']],
        # Short Term Metrics rows
        ["Short Term Hospitalization", facility_info['str_hosp']],
        ["STR National Avg. for Hospitalization", facility_info['str_hosp_nat']],
        ["STR State Avg. for Hospitalization", facility_info['str_hosp_state']],
        ["STR ED Visit", facility_info['str_ed']],
        ["STR ED Visits National Avg.", facility_info['str_ed_nat']],
        ["STR ED Visits State Avg.", facility_info['str_ed_state']],
        # Long Term Metrics rows
        ["LT Hospitalization", facility_info['lt_hosp']],
        ["LT National Avg. for Hospitalization", facility_info['lt_hosp_nat']],
        ["LT State National Avg. for Hospitalization", facility_info['lt_hosp_state']],
        ["ED Visit", facility_info['lt_ed']],
        ["LT ED Visits National Avg.", facility_info['lt_ed_nat']],
        ["LT ED Visits State Avg.", facility_info['lt_ed_state']],
    ]
    
    table = Table(report_data, colWidths=[240, 300])
    table.setStyle(TableStyle([
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        # Set padding to 2.5 to cleanly keep all 26 lines + logo on ONE pristine page
        ('BOTTOMPADDING', (0,0), (-1,-1), 2.5),
        ('TOPPADDING', (0,0), (-1,-1), 2.5),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
    ]))
    story.append(table)
    story.append(Spacer(1, 8))
    
    # Clickable Source Link
    ccn = manual_data['ccn']
    medicare_url = f"https://www.medicare.gov/care-compare/details/nursing-home/{ccn}"
    link_html = f'<font color="blue"><u>Click here to view official Medicare Care Compare Profile</u></font>'
    story.append(Paragraph(f'<b>Source Link:</b> <a href="{medicare_url}">{link_html}</a>', body_style))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


# --- FRONTEND INTERFACE ---
st.set_page_config(page_title="Medelite Report Tool", layout="centered")

# Render Logo cleanly on the app screen
st.markdown("<br>", unsafe_allow_html=True)
if os.path.exists("logo.png"):
    col_img, _ = st.columns([1, 4])
    with col_img:
        st.image("logo.png", width=70)
else:
    st.markdown("<h3 style='text-align: center;'>INFINITE — Managed by MEDELITE</h3>", unsafe_allow_html=True)

st.title(" Localized Micro-App Generator")
cnn_input = st.text_input("Enter 6-Digit CCN Code:", placeholder="e.g., 686123")

if cnn_input:
    facility_info = get_cms_facility_data(cnn_input)
    
    if facility_info:
        st.success(f" Loaded: {facility_info['legal_name']}")
        
        st.subheader(" Operational Inputs Override Dashboard")
        override_name = st.text_input("Facility Name Override (Optional):")
        
        col1, col2 = st.columns(2)
        with col1:
            emr = st.text_input("EMR:", value="PCC")
            current_census = st.text_input("Current Census:", value="112")
            patient_type = st.text_input("Type of Patient:", value="Long-term & Short-term")
        with col2:
            medelite_history = st.selectbox("Previous Coverage from Medelite:", ["Yes", "No"])
            medelite_perf = st.text_input("Previous Provider Performance from Medelite:", value="About 30 patients/day")
            medical_coverage = st.text_input("Medical Coverage Options:", value="Optometry, PCP, Podiatry")
            
        manual_inputs = {
            "ccn": cnn_input, "override_name": override_name, "emr": emr,
            "current_census": current_census, "patient_type": patient_type,
            "medelite_history": medelite_history, "medelite_perf": medelite_perf,
            "medical_coverage": medical_coverage
        }
        
        st.subheader(" Action Center")
        pdf_data = create_pdf_report(facility_info, manual_inputs)
        
        st.download_button(
            label=" Generate & Download Polished PDF Report",
            data=pdf_data,
            file_name=f"Medelite_Assessment_{cnn_input}.pdf",
            mime="application/pdf"
        )
    else:
        st.error(" No data matches that identifier.")