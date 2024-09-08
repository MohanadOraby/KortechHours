import pandas as pd
from datetime import timedelta
import streamlit as st


def preprocess_file(file_path):
  # Load excel file
  df = pd.read_excel(file_path)

  # Some cleaning
  df = df.drop(columns=['Day','Requested','Deduction','Request'])
  df = df.dropna(subset=['In','Out'], how='all')
  df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce')
  df['Date'] = df['Date'].dt.strftime('%d/%m/%Y')

  # Fixing columns "In" and "Out" and changing it to datetime
  df['In'] = pd.to_datetime(df['In'], format='%I:%M%p')
  df['Out'] = pd.to_datetime(df['Out'], format='%I:%M%p')

  # Calculating hours worked and hours required
  df['Hours_worked'] = (df['Out'] - df['In'])
  total_seconds = df['Hours_worked'].sum().total_seconds()
  WHours = int(total_seconds // (60*60))
  WMinutes = int(total_seconds % (60*60) // 60)
  RHours = int(df.shape[0]*8.5)
  RMinutes = int((df.shape[0]*8.5*60 ) % 60)
  days_worked = df.shape[0]

  # Print
  return {
      "hours_required": f"{RHours}:{RMinutes:02}",
      "hours_worked": f"{WHours}:{WMinutes:02}",
      "total_hours_worked": WHours + WMinutes / 60,  # For comparison, will not be displayed
      "total_hours_required": RHours + RMinutes / 60, # For comparison, will not be displayed
      "days_worked": days_worked
  }


# Adding a title to the webpage
st.set_page_config(page_title="Work Hours Tracker", page_icon="🕒")  # Set the page title and icon
st.title("KORTECH Work Hours Tracker")  # Main title on the app

# Adding a prompt for users to upload the Excel file
st.write("Please upload your Excel file to calculate work hours.")

# File uploader prompt
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Process File"):
        results = preprocess_file(uploaded_file)

        # Display the results using st.write()
        st.subheader("Results:")
        st.write(f"**Number of hours required:** {results['hours_required']}")
        st.write(f"**Number of hours worked:** {results['hours_worked']}")
        st.write(f"**Number of days worked:** {results['days_worked']}")

        # Compare hours worked and hours required
        if results['total_hours_worked'] >= results['total_hours_required']:
            # Display "YOU ARE SAFE" in green
            st.markdown("<h1 style='text-align: center; color: green;'>YOU ARE SAFE</h1>", unsafe_allow_html=True)
        else:
            # Display "NOT SAFE" in red
            st.markdown("<h1 style='text-align: center; color: red;'>NOT SAFE</h1>", unsafe_allow_html=True)
