import io
import math
from typing import Tuple

import pandas as pd
from fpdf import FPDF


def compute_quantity(l: float, b: float, h: float) -> Tuple[float, str]:
    ft_to_m = 0.3048
    l_m = l * ft_to_m
    b_m = b * ft_to_m
    h_m = h * ft_to_m
    if h <= 0 or math.isclose(h, 1.0, rel_tol=1e-2) or h_m <= ft_to_m:
        if b <= 0 or math.isclose(b, 1.0, rel_tol=1e-2) or b_m <= ft_to_m:
            return l_m, "rmt"
        return l_m * b_m, "sqm"
    return l_m * b_m * h_m, "cum"


def material_breakup(quantity: float) -> Tuple[float, float, float]:
    return quantity * 7.0, quantity * 0.42, quantity * 0.83


def calculate_cp_gst(total: float, cp_percent: float, gst_percent: float) -> Tuple[float, float, float]:
    total_after_cp = total * (1 - cp_percent / 100.0)
    gst_amount = total_after_cp * (gst_percent / 100.0)
    final_total = total_after_cp + gst_amount
    return total_after_cp, gst_amount, final_total


def save_to_excel(df: pd.DataFrame, material_df: pd.DataFrame, abstract_df: pd.DataFrame) -> bytes:
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name="BOQ", index=False)
        material_df.to_excel(writer, sheet_name="Materials", index=False)
        abstract_df.to_excel(writer, sheet_name="Abstract", index=False)
    return output.getvalue()


class _PDFBuilder(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(0, 10, "Civil Engineering Estimation Report", ln=1, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 8)
        self.cell(0, 10, "Page %s" % self.page_no(), align="C")


def build_pdf(df: pd.DataFrame, material_df: pd.DataFrame, abstract_df: pd.DataFrame) -> bytes:
    pdf = _PDFBuilder(orientation="L", unit="mm", format="A4")
    pdf.add_page()
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Bill of Quantities", ln=1)
    pdf.set_font("Arial", size=8)
    page_width = pdf.w - 20
    col_widths = [page_width / df.shape[1]] * df.shape[1]
    for i, column in enumerate(df.columns):
        pdf.cell(col_widths[i], 6, str(column), border=1, align="C")
    pdf.ln()
    for _, row in df.iterrows():
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 6, str(cell), border=1)
        pdf.ln()
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Material Summary", ln=1)
    pdf.set_font("Arial", size=8)
    if not material_df.empty:
        col_widths = [page_width / material_df.shape[1]] * material_df.shape[1]
        for i, column in enumerate(material_df.columns):
            pdf.cell(col_widths[i], 6, str(column), border=1, align="C")
        pdf.ln()
        for _, row in material_df.iterrows():
            for i, cell in enumerate(row):
                pdf.cell(col_widths[i], 6, str(cell), border=1)
            pdf.ln()
    else:
        pdf.cell(0, 6, "No volume items", border=1, ln=1)
    pdf.ln(4)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, "Abstract of Cost", ln=1)
    pdf.set_font("Arial", size=8)
    col_widths = [page_width / abstract_df.shape[1]] * abstract_df.shape[1]
    for i, column in enumerate(abstract_df.columns):
        pdf.cell(col_widths[i], 6, str(column), border=1, align="C")
    pdf.ln()
    for _, row in abstract_df.iterrows():
        for i, cell in enumerate(row):
            pdf.cell(col_widths[i], 6, str(cell), border=1)
        pdf.ln()
    content = pdf.output(dest="S")
    if isinstance(content, (bytes, bytearray)):
        return bytes(content)
    return content.encode("latin-1")
