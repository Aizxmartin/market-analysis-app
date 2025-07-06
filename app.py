import streamlit as st
import pandas as pd
from docx import Document
from datetime import date
import tempfile
import base64
import fitz  # PyMuPDF

def analyze_market(df):
    # Specify your MLS export column names
    PRICE_COLUMN = 'close price'
    SQFT_COLUMN = 'above grade finished area'

    comps = df.copy()
    comps['PricePerSF'] = comps[PRICE_COLUMN] / comps[SQFT_COLUMN]
    avg_ppsf = comps['PricePerSF'].mean()
    return comps, avg_ppsf

def extract_pdf_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    all_text = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        all_text.append(f"--- Subject Property Details - Page {page_num} ---\n{text}\n")
    return "\n".join(all_text)

def generate_report(subject_info, comps, est_ppsf, notes, zillow_val, redfin_val, pdf_text):
    doc = Document()
    doc.add_heading('Market Valuation Report', 0)
    doc.add_paragraph(f"Date: {date.today().strftime('%B %d, %Y')}")

    doc.add_heading('Subject Property', level=1)
    doc.add_paragraph(f"Address: {subject_info['address']}")
    doc.add_paragraph(
        f"SqFt: {subject_info['sqft']}, Beds: {subject_info['beds']}, Baths: {subject_info['baths']}"
    )
    doc.add_paragraph(f"Close Price: ${subject_info['price']:,.0f}")

    est_subject_price = est_ppsf * subject_info['sqft']
    doc.add_heading('Estimated Market Value Based on Comps', level=1)
    doc.add_paragraph(f"Average Price per SqFt: ${est_ppsf:,.2f}")
    doc.add_paragraph(f"Estimated Value: ${est_subject_price:,.0f}")

    doc.add_heading('Public Online Estimates', level=1)
    doc.add_paragraph(f"Zillow Zestimate: ${zillow_val}")
    doc.add_paragraph(f"Redfin Estimate: ${redfin_val}")

    doc.add_heading('Notes and Special Features', level=1)
    doc.add_paragraph(notes)

    doc.add_heading('Comparable Properties', level=1)
    for _, row in comps.iterrows():
        doc.add_paragraph(
            f"{row['address']}: ${row['close price']:,.0f} | {row['above grade finished area']} SqFt | {row['bedrooms total']} Bd / {row['bathrooms total integer']} Ba",
            style='List Bullet'
        )

    if pdf_text:
        doc.add_heading('Subject Property Details (from PDF)', level=1)
        doc.add_paragraph(pdf_text) 
        
    return doc

def main():
    st.title("Market Analysis Report Generator")

    st.write("Upload your MLS data (CSV) and Subject Property PDF:")

    csv_file = st.file_uploader("Upload CSV file", type=["csv"])
    pdf_file = st.file_uploader("Upload Subject Property PDF", type=["pdf"])

    # Gather user inputs
    subject_address = st.text_input("Subject Property Address")
    subject_sqft = st.number_input("Subject Property SqFt", min_value=0, step=1)
    subject_beds = st.number_input("Bedrooms", min_value=0, step=1)
    subject_baths = st.number_input("Bathrooms", min_value=0, step=1)
    subject_price = st.number_input("Closed Price", min_value=0, step=1)

    zillow_val = st.text_input("Zillow Estimate")
    redfin_val = st.text_input("Redfin Estimate")
    notes = st.text_area("Notes and Special Features")

    if st.button("Generate Report"):
        if csv_file and pdf_file:
            df = pd.read_csv(csv_file)
            comps, avg_ppsf = analyze_market(df)
            pdf_text = extract_pdf_text(pdf_file)

            subject_info = {
                "address": subject_address,
                "sqft": subject_sqft,
                "beds": subject_beds,
                "baths": subject_baths,
                "price": subject_price
            }

            # Generate Word doc
            doc = generate_report(subject_info, comps, avg_ppsf, notes, zillow_val, redfin_val, pdf_text)

            # Save to temp file and download
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".docx")
            doc.save(tmp.name)

            with open(tmp.name, "rb") as f:
                b64 = base64.b64encode(f.read()).decode()
                href = f'<a href="data:application/octet-stream;base64,{b64}" download="market_report.docx">Download Report</a>'
                st.markdown(href, unsafe_allow_html=True)
        else:
            st.error("Please upload both CSV and PDF files.")

if __name__ == "__main__":
    main()
