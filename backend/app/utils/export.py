import pandas as pd
from fpdf import FPDF
import io

def generate_excel_report(data_dicts):
    df = pd.DataFrame(data_dicts)
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Attendance')
    return output.getvalue()

def generate_pdf_report(data_dicts, class_info="", date_info=""):
    pdf = FPDF()
    pdf.add_page()
    
    # Title
    pdf.set_font("Helvetica", size=16, style='B')
    pdf.cell(200, 10, txt="Attendance Report", new_x="LMARGIN", new_y="NEXT", align='C')
    
    # Subtitle
    pdf.set_font("Helvetica", size=12)
    pdf.cell(200, 10, txt=f"Class: {class_info} | Date: {date_info}", new_x="LMARGIN", new_y="NEXT", align='C')
    
    pdf.ln(10)
    
    if not data_dicts:
        pdf.cell(200, 10, txt="No records found.", new_x="LMARGIN", new_y="NEXT", align='C')
        return bytes(pdf.output())
    
    # Table Header
    headers = list(data_dicts[0].keys())
    col_widths = [190 / max(len(headers), 1)] * len(headers)
    
    pdf.set_font("Helvetica", size=10, style='B')
    for i, header in enumerate(headers):
        new_x = "RIGHT" if i < len(headers) - 1 else "LMARGIN"
        new_y = "TOP" if i < len(headers) - 1 else "NEXT"
        pdf.cell(col_widths[i], 10, txt=str(header), border=1, align='C', new_x=new_x, new_y=new_y)
    
    # Table Data
    pdf.set_font("Helvetica", size=10)
    for row in data_dicts:
        for i, header in enumerate(headers):
            val = str(row.get(header, ''))
            new_x = "RIGHT" if i < len(headers) - 1 else "LMARGIN"
            new_y = "TOP" if i < len(headers) - 1 else "NEXT"
            pdf.cell(col_widths[i], 10, txt=val[:25], border=1, align='C', new_x=new_x, new_y=new_y)
    
    return bytes(pdf.output())

