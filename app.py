
import streamlit as st
import pandas as pd
from docx import Document
from datetime import date
import tempfile
import base64

def analyze_market(df, subject_address):
    comps = df[df['Address'] != subject_address].copy()
    subject = df[df['Address'] == subject_address].iloc[0]
    comps['PricePerSF'] = comps['Price'] / comps['SqFt']
    avg_ppsf = comps['PricePerSF'].mean()
    est_subject_price = avg_ppsf * subject['SqFt']
    return subject, comps, est_subject_price

def generate_report(subject, comps, est_price, notes, zillow_val, redfin_val):
    doc = Document()
    doc.add_heading('Market Valuation Report', 0)
    doc.add_paragraph(f"Date: {date.today().strftime('%B %d, %Y')}")

    doc.add_heading('Subject Property', level=1)
    doc.add_paragraph(f"Address: {subject['Address']}")
    doc.add_paragraph(f"SqFt: {subject['SqFt']}, Beds: {subject['Beds']}, Baths: {subject['Baths']}")

    doc.add_heading('Estimated Market Value', level=1)
    doc.add_paragraph(f"Estimated Price Based on Comps: ${est_price:,.0f}")

    doc.add_heading('Public Online Estimates', level=1)
    doc.add_paragraph(f"Zillow Zestimate: ${zillow_val}")
    doc.add_paragraph(f"Redfin Estimate: ${redfin_val}")

    doc.add_heading('Notes and Special Features', level=1)
    doc.add_paragraph(notes)

    doc.add_heading('Comparable Properties', level=1)
    for _, row in comps.iterrows():
        doc.add_paragraph(
            f"{row['Address']}: ${row['Price']:,.0f} | {row['SqFt']} SqFt | {row['Beds']} Bd / {row['Baths']} Ba",
            style='List Bullet'
        )

    doc.add_paragraph("\n---\n")
    doc.add_paragraph("This is an estimate based on MLS market information and publicly available data. It is intended for marketing and informational purposes only and does not constitute an appraisal or guarantee of market value.")

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
    doc.save(temp_file.name)
    return temp_file.name

st.title("📊 Cloud Market Valuation Tool")
st.write("Upload MLS data, enter subject details, and generate a branded market report.")

uploaded_file = st.file_uploader("Upload MLS CSV File", type=["csv"])
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.write("Preview of Data:", df.head())

    subject_address = st.selectbox("Select Subject Property Address", df['Address'].unique())
    notes = st.text_area("Enter Notes and Special Features")
    zillow_val = st.text_input("Zillow Zestimate")
    redfin_val = st.text_input("Redfin Estimate")

    if st.button("Generate Report"):
        subject, comps, est_price = analyze_market(df, subject_address)
        report_path = generate_report(subject, comps, est_price, notes, zillow_val, redfin_val)

        with open(report_path, "rb") as f:
            b64 = base64.b64encode(f.read()).decode()
            href = f'<a href="data:application/octet-stream;base64,{b64}" download="Market_Valuation_Report.docx">📄 Download Report</a>'
            st.markdown(href, unsafe_allow_html=True)
