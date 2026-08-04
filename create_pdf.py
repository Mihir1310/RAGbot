import os
from fpdf import FPDF

def create_sample_pdf():
    os.makedirs("data", exist_ok=True)
    pdf_path = "data/sample_10k.pdf"

    if os.path.exists(pdf_path):
        return pdf_path

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=15)
    pdf.cell(200, 10, txt="ACME Corp - Annual Form 10-K", ln=1, align='C')
    pdf.set_font("Arial", size=12)

    content = """
    Item 1. Business
    ACME Corp is a leading manufacturer of anvils and explosive tennis balls.

    Item 1A. Risk Factors
    We face significant risks, particularly related to the road runner demographic. Supply chain issues have delayed our giant rubber band shipments by 12%.

    Item 7. Management's Discussion and Analysis of Financial Condition and Results of Operations
    This year, our revenue increased by 5% to $1.2 billion, driven primarily by the strong performance of our rocket-powered roller skates division. However, operating expenses rose 8% due to increased legal settlements.
    """

    pdf.multi_cell(0, 10, txt=content)
    pdf.output(pdf_path)
    return pdf_path

if __name__ == "__main__":
    create_sample_pdf()
