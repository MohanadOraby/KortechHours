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
  Hours = int(total_seconds // (60*60))
  Minutes = int(total_seconds % (60*60) // 60)

  # Print
  return {
  print(f"Hours Required: {int(df.shape[0]*8.5)}:{int((df.shape[0]*8.5*60 ) % 60):02}"),
  print(f"Hours Worked: {Hours}:{Minutes:02}"),
  print(f"Days Worked: {df.shape[0]}")
  }


# Adding a title to the webpage
st.set_page_config(page_title="Work Hours Tracker", page_icon="🕒")  # Set the page title and icon
st.title("KORTECH Work Hours Tracker")  # Main title on the app

# Adding a prompt for users to upload the Excel file
st.write("Please upload your Excel file to calculate work hours.")

# File uploader prompt
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    results = preprocess_file(uploaded_file)
