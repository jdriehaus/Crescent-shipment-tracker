import streamlit as st
import pandas as pd
import datetime
import io

# Load the Excel data
def load_data():
    file_path = "C1 Door and Lot Log.xlsx"
    xls = pd.ExcelFile(file_path)
    st.write("Available sheet names:", xls.sheet_names)  # Debug line
    df = xls.parse(xls.sheet_names[0], dtype=str)  # Load first sheet by default
    df = df.dropna(how="all")  # Drop completely empty rows
    return df

def save_data(df):
    df.to_excel("C1 Door and Lot Log.xlsx", index=False)

# App layout
st.title("Dock Door & Lot Log Tracker")

data = load_data()
st.dataframe(data)

st.header("Add New Shipment Entry")

with st.form("shipment_form"):
    door = st.text_input("Door")
    trailer_no = st.text_input("Trailer No")
    ro_no = st.text_input("RO No")
    direction = st.selectbox("Inbound or Outbound", ["Inbound", "Outbound", "Storage", "Racking", "Other"])
    customer = st.text_input("Customer")
    comments = st.text_input("Comments")
    drop_date = st.date_input("Drop Date", value=datetime.date.today())

    submitted = st.form_submit_button("Add Entry")

    if submitted:
        new_entry = pd.DataFrame({
            "Door": [door],
            "Trailer No": [trailer_no],
            "RO No": [ro_no],
            "Inbound/Outbound": [direction],
            "Customer": [customer],
            "Comments": [comments],
            "Drop Date": [pd.to_datetime(drop_date)]
        })
        updated_data = pd.concat([data, new_entry], ignore_index=True)
        save_data(updated_data)
        st.success("Shipment entry added successfully! Please refresh the app to see updates.")

st.header("Search Shipments")
with st.expander("Filter Options"):
    customer_filter = st.text_input("Filter by Customer")
    date_range = st.date_input("Filter by Drop Date Range", [])

    filtered_data = data.copy()
    if customer_filter:
        filtered_data = filtered_data[filtered_data["Customer"].str.contains(customer_filter, case=False, na=False)]
    if len(date_range) == 2:
        start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_data = filtered_data[(filtered_data["Drop Date"] >= start) & (filtered_data["Drop Date"] <= end)]

    st.dataframe(filtered_data)

# Prepare Excel download using in-memory buffer
output = io.BytesIO()
with pd.ExcelWriter(output, engine='openpyxl') as writer:
    filtered_data.to_excel(writer, index=False)
output.seek(0)

st.download_button(
    label="Download Current View as Excel",
    data=output,
    file_name="Filtered_Shipments.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)
