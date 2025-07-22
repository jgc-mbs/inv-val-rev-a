import streamlit as st
import pandas as pd
import pdfplumber
import io

# Placeholder for the validation function
def validate_invoice(df):
    results = df.copy()
    results['Validation'] = 'Valid'  # Replace with real logic
    return results

st.title("Commercial Invoice Validation Tool")
st.write("Upload your commercial invoice (PDF, CSV, or Excel) to validate HS codes and other fields.")

uploaded_file = st.file_uploader("Choose a file", type=["pdf", "csv", "xlsx"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        elif uploaded_file.name.endswith('.xlsx'):
            df = pd.read_excel(uploaded_file, engine='openpyxl')
        elif uploaded_file.name.endswith('.pdf'):
            with pdfplumber.open(uploaded_file) as pdf:
                all_tables = []
                for page in pdf.pages:
                    tables = page.extract_tables()
                    for table in tables:
                        if table:
                            df_page = pd.DataFrame(table[1:], columns=table[0])
                            all_tables.append(df_page)
                if all_tables:
                    df = pd.concat(all_tables, ignore_index=True)
                else:
                    st.warning("No tables found in the PDF.")
                    df = None
        else:
            st.error("Unsupported file format.")
            df = None

        if df is not None:
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
