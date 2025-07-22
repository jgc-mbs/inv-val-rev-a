import streamlit as st
import pandas as pd
import pdfplumber

# Placeholder for the validation function
def validate_invoice(df):
    results = df.copy()
    results['Validation'] = 'Valid'  # Replace with real logic
    return results

def extract_valid_table_from_pdf(file):
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            tables = page.extract_tables()
            for table in tables:
                if table and len(table) > 1:
                    df = pd.DataFrame(table[1:], columns=table[0])
                    # Check for duplicate or mostly empty headers
                    if df.columns.duplicated().any() or all(col is None or str(col).strip() == '' for col in df.columns):
                        continue
                    return df
    return None

st.title("Commercial Invoice Validation Tool")
st.write("Upload your commercial invoice (PDF, CSV, or Excel) to validate HS codes and other fields.")

uploaded_file = st.file_uploader("Choose a file", type=["csv", "xlsx", "pdf"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.name.endswith('.pdf'):
            df = extract_valid_table_from_pdf(uploaded_file)
            if df is None:
                st.warning("No valid table found in the PDF.")
                st.stop()
        else:
            st.error("Unsupported file type.")
            st.stop()

        st.subheader("Uploaded Invoice Preview")
        st.dataframe(df)

        validated_df = validate_invoice(df)

        st.subheader("Validation Results")
        st.dataframe(validated_df)

        csv = validated_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Validation Report",
            data=csv,
            file_name="validation_report.csv",
            mime="text/csv"
        )
    except Exception as e:
        st.error(f"Error processing file: {e}")
