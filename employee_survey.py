import streamlit as st
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import re

# Google Sheets setup using Streamlit Secrets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
json_data = dict(st.secrets["credentials"])
creds = ServiceAccountCredentials.from_json_keyfile_dict(json_data, scope)
client = gspread.authorize(creds)
sheet = client.open("Employee Survey Responses").sheet1

# -------------------------------
# Helper functions for validation
# -------------------------------
def is_valid_email(email):
    pattern = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return re.match(pattern, email)

def is_valid_phone(phone):
    return phone.startswith("+971") and len(phone) == 13 and phone[4:].isdigit()

# -------------------------------
# Streamlit Form UI
# -------------------------------
st.title("Employed Nomination Form")

adge_name = st.text_input("Name of ADGE")
num_employees = st.number_input("Number of nominated employees:", min_value=1, step=1)

employee_data = []
submission_error = False

for i in range(num_employees):
    st.subheader(f"Employee {i + 1}")
    name = st.text_input("Full Name", key=f"name_{i}")
    designation = st.text_input("Designation", key=f"designation_{i}") 
    email = st.text_input("Email Address", key=f"email_{i}")
    phone = st.text_input("Phone Number", value="+971", key=f"phone_{i}")


    employee_data.append({
        "Name": name,
        "Designation": designation,  
        "Email": email,
        "Phone": phone
    })

# -------------------------------
# Submission logic
# -------------------------------
if st.button("Submit"):
    if not adge_name.strip():
        st.error("The 'Name of ADGE' field is required.")
        submission_error = True

    for idx, emp in enumerate(employee_data):
        if not emp["Name"].strip():
            st.error(f"Full Name is required for Employee {idx + 1}.")
            submission_error = True
        if not emp["Designation"].strip():
            st.error(f"Designation is required for Employee {idx + 1}.")  
            submission_error = True
        if not is_valid_email(emp["Email"]):
            st.error(f"Invalid Email Address for Employee {idx + 1}.")
            submission_error = True
        if not is_valid_phone(emp["Phone"]):
            st.error(f"Invalid phone number for Employee {idx + 1}. It must start with +971 and include exactly 9 digits after.")
    
            submission_error = True

    if not submission_error:
        existing_rows = sheet.get_all_values()
        duplicates = []
        submitted = []

        for idx, emp in enumerate(employee_data):
            row = [adge_name, emp["Name"], emp["Designation"], emp["Email"], emp["Phone"]]

            if row in existing_rows:
                duplicates.append(idx + 1)  # Store employee number
            else:
                sheet.append_row(row)
                submitted.append(idx + 1)

        if submitted:
            st.success(f"Successfully submitted entries for: Employee(s) {', '.join(map(str, submitted))}")

        if duplicates:
            st.warning(f"Duplicate entries found. Skipped Employee(s): {', '.join(map(str, duplicates))}")
