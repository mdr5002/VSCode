import pdfplumber
import pandas as pd


def extract_data_with_pdfplumber(pdf_path):
    """
    Extracts data from a PDF file using pdfplumber.
    This function extracts the company number from text and tables from the PDF.
    """
    all_text = ""
    all_tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            # Extract text
            text = page.extract_text()
            if text:
                all_text += text + "\n"

            # Extract table
            table = page.extract_table()
            if table:
                # Convert table to DataFrame and append to list
                df = pd.DataFrame(table[1:], columns=table[0])
                all_tables.append(df)

    # Extract company number from all_text
    company_number = extract_company_number(
        all_text
    )  # Use the previously defined function or similar logic

    # Combine all tables into a single DataFrame
    if all_tables:
        combined_df = pd.concat(all_tables, ignore_index=True)
        combined_df["Company Number"] = (
            company_number  # Add the company number to each row
        )
        return combined_df
    else:
        return pd.DataFrame(
            columns=["Company Number"]
        )  # Return an empty DataFrame if no table is found


# Define the path to your PDF file(s)
pdf_path = "C:\\Users\\mrice\\OneDrive - Kalas Manufacturing Inc\\Documents - Kalas Pricing\\Price Lists\\Bulk\\2-01-2024 Price Lists\\"

# Example usage
df = extract_data_with_pdfplumber(pdf_path)
print(df.head())

# Now combined_df contains all the data with a company number column
