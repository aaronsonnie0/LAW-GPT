import os
import base64
import tempfile
import pandas as pd

# Try to import optional dependencies
try:
    from fpdf import FPDF
    FPDF_AVAILABLE = True
except ImportError:
    FPDF_AVAILABLE = False
    print("FPDF not available. PDF export will be disabled.")

class ExportUtils:
    """
    Utilities for exporting document analysis
    """

    @staticmethod
    def create_pdf_report(document_name, summary, clauses, high_risk_clauses=None):
        """
        Create a PDF report of the document analysis

        Args:
            document_name: Name of the document
            summary: Document summary
            clauses: List of clause dictionaries
            high_risk_clauses: List of high-risk clause dictionaries

        Returns:
            Path to the generated PDF file or None if FPDF is not available
        """
        if not FPDF_AVAILABLE:
            print("Cannot create PDF report: FPDF is not installed. Please install it with: pip install fpdf")
            return None

        try:
            pdf = FPDF()
            pdf.add_page()

            # Set up fonts
            pdf.set_font("Arial", "B", 16)

            # Title
            pdf.cell(0, 10, f"Legal Analysis Report: {document_name}", 0, 1, "C")
            pdf.ln(10)

            # Summary
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "Document Summary", 0, 1, "L")
            pdf.set_font("Arial", "", 12)

            # Split summary into lines to fit in PDF
            summary_lines = summary.split('\n')
            for line in summary_lines:
                # Handle markdown headers
                if line.startswith('# '):
                    pdf.set_font("Arial", "B", 14)
                    pdf.cell(0, 10, line[2:], 0, 1, "L")
                    pdf.set_font("Arial", "", 12)
                elif line.startswith('## '):
                    pdf.set_font("Arial", "B", 13)
                    pdf.cell(0, 10, line[3:], 0, 1, "L")
                    pdf.set_font("Arial", "", 12)
                elif line.startswith('### '):
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, line[4:], 0, 1, "L")
                    pdf.set_font("Arial", "", 12)
                # Handle bullet points
                elif line.strip().startswith('- '):
                    pdf.cell(10, 10, "", 0, 0)
                    pdf.cell(0, 10, line.strip()[2:], 0, 1)
                # Regular text
                elif line.strip():
                    pdf.multi_cell(0, 10, line)

            pdf.ln(10)

            # High-risk clauses
            if high_risk_clauses and len(high_risk_clauses) > 0:
                pdf.add_page()
                pdf.set_font("Arial", "B", 14)
                pdf.cell(0, 10, "High-Risk Clauses", 0, 1, "L")
                pdf.ln(5)

                for clause in high_risk_clauses:
                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, f"Clause {clause['id']} - {clause.get('type', 'Unknown')}", 0, 1, "L")

                    pdf.set_font("Arial", "", 12)
                    pdf.multi_cell(0, 10, clause['text'])

                    pdf.set_font("Arial", "B", 12)
                    pdf.cell(0, 10, "Risk Analysis:", 0, 1, "L")

                    pdf.set_font("Arial", "", 12)
                    risk_analysis_lines = clause.get('risk_analysis', '').split('\n')
                    for line in risk_analysis_lines:
                        if line.strip().startswith('- '):
                            pdf.cell(10, 10, "", 0, 0)
                            pdf.cell(0, 10, line.strip()[2:], 0, 1)
                        elif line.strip():
                            pdf.multi_cell(0, 10, line)

                    pdf.ln(10)

            # All clauses
            pdf.add_page()
            pdf.set_font("Arial", "B", 14)
            pdf.cell(0, 10, "All Clauses", 0, 1, "L")
            pdf.ln(5)

            # Create a table of clauses
            clause_data = []
            for clause in clauses:
                clause_data.append({
                    "ID": clause.get("id", ""),
                    "Type": clause.get("type", "Unknown"),
                    "Risk Score": clause.get("risk_score", 0)
                })

            # Sort clauses by ID
            clause_data.sort(key=lambda x: x["ID"])

            # Create table headers
            pdf.set_font("Arial", "B", 12)
            pdf.cell(20, 10, "ID", 1, 0, "C")
            pdf.cell(80, 10, "Type", 1, 0, "C")
            pdf.cell(30, 10, "Risk Score", 1, 1, "C")

            # Create table rows
            pdf.set_font("Arial", "", 12)
            for clause in clause_data:
                pdf.cell(20, 10, str(clause["ID"]), 1, 0, "C")
                pdf.cell(80, 10, clause["Type"], 1, 0, "C")
                pdf.cell(30, 10, str(clause["Risk Score"]), 1, 1, "C")

            # Save the PDF to a temporary file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                pdf_path = tmp_file.name

            pdf.output(pdf_path)

            return pdf_path
        except Exception as e:
            print(f"Error creating PDF report: {e}")
            return None

    @staticmethod
    def get_csv_download_link(df, filename="data.csv"):
        """
        Generate a download link for a CSV file

        Args:
            df: Pandas DataFrame
            filename: Name of the CSV file

        Returns:
            HTML link for downloading the CSV
        """
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">Download CSV</a>'
        return href

    @staticmethod
    def get_pdf_download_link(pdf_path, filename="report.pdf"):
        """
        Generate a download link for a PDF file

        Args:
            pdf_path: Path to the PDF file
            filename: Name of the PDF file

        Returns:
            HTML link for downloading the PDF
        """
        with open(pdf_path, "rb") as f:
            pdf_bytes = f.read()

        b64 = base64.b64encode(pdf_bytes).decode()
        href = f'<a href="data:application/pdf;base64,{b64}" download="{filename}">Download PDF Report</a>'
        return href
