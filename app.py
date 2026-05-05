from datetime import datetime

import pandas as pd
import streamlit as st

from utils import compute_quantity, material_breakup, calculate_cp_gst, save_to_excel, build_pdf


def empty_items():
    return pd.DataFrame(
        columns=[
            "Description",
            "Length (ft)",
            "Breadth (ft)",
            "Height (ft)",
            "Quantity",
            "Unit",
            "Rate",
            "Amount",
            "Carriage",
            "Total Amount",
        ]
    )


def recalc(df, carriage_rate, cp_percent, gst_percent):
    rows = []
    for _, row in df.iterrows():
        desc = row.get("Description", "")
        l = float(row.get("Length (ft)", 0) or 0)
        b = float(row.get("Breadth (ft)", 0) or 0)
        h = float(row.get("Height (ft)", 0) or 0)
        rate = float(row.get("Rate", 0) or 0)
        qty, unit = compute_quantity(l, b, h)
        amount = qty * rate
        carriage = qty * carriage_rate
        _, _, final_total = calculate_cp_gst(amount + carriage, cp_percent, gst_percent)
        rows.append(
            {
                "Description": desc,
                "Length (ft)": l,
                "Breadth (ft)": b,
                "Height (ft)": h,
                "Quantity": round(qty, 3),
                "Unit": unit,
                "Rate": rate,
                "Amount": round(amount, 2),
                "Carriage": round(carriage, 2),
                "Total Amount": round(final_total, 2),
            }
        )
    return pd.DataFrame(rows)


def material_df(items):
    rows = []
    for _, row in items.iterrows():
        qty = float(row.get("Quantity", 0) or 0)
        unit = row.get("Unit", "")
        if unit == "cum" and qty > 0:
            cement, sand, agg = material_breakup(qty)
            rows.append(
                {
                    "Item": row.get("Description", ""),
                    "Quantity (m3)": round(qty, 3),
                    "Cement (bags)": round(cement, 2),
                    "Sand (m3)": round(sand, 3),
                    "Aggregate (m3)": round(agg, 3),
                }
            )
    return pd.DataFrame(rows)


def main():
    st.set_page_config(page_title="Estimate App", layout="wide")
    st.title("Civil Engineering Estimation App")

    cp_percent = st.sidebar.number_input("Contractor Profit %", min_value=0.0, value=9.09, step=0.01)
    gst_percent = st.sidebar.number_input("GST %", min_value=0.0, value=5.36, step=0.01)
    carriage_rate = st.sidebar.number_input("Carriage Rate per Unit", min_value=0.0, value=0.0, step=0.01)

    if "items" not in st.session_state:
        st.session_state.items = empty_items()

    st.subheader("Items")
    edited = st.data_editor(st.session_state.items, num_rows="dynamic", use_container_width=True)

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Recalculate"):
            st.session_state.items = recalc(edited, carriage_rate, cp_percent, gst_percent)
            st.rerun()
    with c2:
        if st.button("Reset"):
            st.session_state.items = empty_items()
            st.rerun()

    boq_df = st.session_state.items.copy()
    if not boq_df.empty:
        boq_df.insert(0, "Sl. No", range(1, len(boq_df) + 1))

    st.subheader("Bill of Quantities")
    st.dataframe(boq_df, use_container_width=True)

    mats = material_df(st.session_state.items)
    st.subheader("Material Statement")
    if mats.empty:
        st.info("No volume items to calculate materials.")
    else:
        st.dataframe(mats, use_container_width=True)

    total_amount = float(st.session_state.items["Total Amount"].sum()) if not st.session_state.items.empty else 0.0
    abstract_df = pd.DataFrame([
        {"Description": "Grand Total", "Amount": round(total_amount, 2), "Date": datetime.now().strftime("%d-%m-%Y")}
    ])
    st.subheader("Abstract of Cost")
    st.dataframe(abstract_df, use_container_width=True)

    excel_bytes = save_to_excel(boq_df, mats, abstract_df)
    pdf_bytes = build_pdf(boq_df if not boq_df.empty else pd.DataFrame(columns=["Sl. No"]), mats, abstract_df)

    d1, d2 = st.columns(2)
    with d1:
        st.download_button("Download Excel", excel_bytes, file_name="estimation_report.xlsx")
    with d2:
        st.download_button("Download PDF", pdf_bytes, file_name="estimation_report.pdf")


if __name__ == "__main__":
    main()
