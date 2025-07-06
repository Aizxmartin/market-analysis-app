import streamlit as st
import pandas as pd
from docx import Document
from datetime import date
import tempfile
import base64
import fitz  # PyMuPDF

def analyze_market(df, subject_address):
    comps = df[df['address'] != subject_address].copy()
    subject = df[df['address'] == subject_address].iloc[0]

    # Specify your MLS export column names
    PRICE_COLUMN = 'close price'
    SQFT_COLUMN = 'above grade finished area'

    comps['PricePerSF'] = comps[PRICE_COLUMN] / comps[SQFT_COLUMN]
    avg_ppsf = comps['PricePerSF'].mean()
    est_subject_price = avg_ppsf * subject[SQFT_COLUMN]

    return subject, comps, est_subject_price

def extract_pdf_text(pdf_file):
    doc = fitz.open(stream=pdf_file.read(), filetype="pdf")
    all_text = []
    for page_num, page in enumerate(doc, start=1):
        text = page.get_text()
        all_text.append(f"--- Subject Property Details - Page {page_num} ---\n{text}\n")
    return "\n".join(all_text)

def generate_report(subject, comps, est_price, notes, zillow_val, redfin_val, pdf_text):
    doc = Document()
    doc.add_heading('Market Valuation Report', 0)
    doc.add_paragraph(f"Date: {date.today().strftime('%B %d, %Y')}")

    doc.add_heading('Subject Property', level=1)
    doc.add_paragraph(f"Address: {subject['address']}")
    doc.add_paragraph(
        f"SqFt: {subject['above grade finished area']}, Beds: {subject['bedrooms total']}, Baths: {subject['bathrooms total integer']}"
    )

    doc.add_heading('Estimated Market Value', level=1)
    doc.add_paragraph(f"Estimated Price Based on Comps: ${est_price:,.0f}")

    doc.add_heading('Public Online Estimates', level=1)
    doc.add_paragraph(f"Zillow Zestimate: ${zillow_val}")
    doc.add_paragraph(f"Redfin Estimate: ${redfin_val}")

    doc.add_heading('Notes and Special Features', level=1)
