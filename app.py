import pandas as pd
from datetime import timedelta
import streamlit as st


def preprocess_file_calculation(file_path):
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
  # df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
  last_date = pd.to_datetime(df['Date']).iloc[-1]

  if last_date.day <= 15:
    target_date = last_date.replace(day=15)
  else:
    if last_date.month == 12:
      target_date = last_date.replace(year = last_date.year + 1, month = 1, day = 15)
    else:
      target_date = last_date.replace(month = last_date.month + 1, day = 15)

  # Date range (including weekends)
  date_range = pd.date_range(start=last_date + timedelta(days=1), end=target_date)

  # Exclude weekends (Friday and Saturday)

  working_days = [d for d in date_range if d.weekday() not in  [4,5]] #4 is Friday and 5 is Satuday

  days_until_15th = len(working_days)

  # Print
  return {
      "hours_required": f"{RHours}:{RMinutes:02}",
      "hours_worked": f"{WHours}:{WMinutes:02}",
      "total_hours_worked": WHours + WMinutes / 60,  # For comparison, will not be displayed
      "total_hours_required": RHours + RMinutes / 60, # For comparison, will not be displayed
      "days_worked": days_worked,
      "days_until_15th" : days_until_15th
  }

def preprocess_table_display(file_path):
  # Load excel file
  df_orig = pd.read_excel(file_path)

  # Some cleaning
  df = df_orig.drop(columns=['Day','Requested','Deduction','Request'])
  df = df.dropna(subset=['In','Out'], how='all')
  df['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

  # Fixing columns "In" and "Out" and changing it to datetime
  df['In'] = pd.to_datetime(df['In'], format='%I:%M%p')
  df['Out'] = pd.to_datetime(df['Out'], format='%I:%M%p')
  
  # Calculate Hours_worked
  df['Hours_worked'] = (df['Out'] - df['In'])

  # Fixing display of hours_worked
  df['Hours_worked'] = df['Hours_worked'].astype(str).str.replace('0 days ', '', regex=False)

  # Fixing display of In and Out
  df['In'] = df['In'].dt.time
  df['Out'] = df['Out'].dt.time

  df_orig['Date'] = pd.to_datetime(df['Date'], dayfirst=True, errors='coerce').dt.strftime('%Y-%m-%d')

  # Fixing day name
  df_orig['Day'] = pd.to_datetime(df_orig['Date']).dt.day_name()
  df['Day'] = pd.to_datetime(df['Date']).dt.day_name()

  df_merged = pd.merge(df_orig, df[['Date','Hours_worked','Day']], on=['Date','Day'], how='left')

  df_merged.drop(columns =['Requested','Deduction','Request'] , inplace=True)

  return df_merged


# Streamlit App
st.set_page_config(page_title="Work Hours Tracker", page_icon="🕒")  # Set the page title and icon
st.title("KORTECH Work Hours Tracker")  # Main title on the app


# Adding a prompt for users to upload the Excel file
st.write("PLEASE MAKE SURE ALL 'IN' AND 'OUT' COLUMNS ARE FILLED WITH VALUES FOR ACCURATE RESULTS")

# File uploader prompt
uploaded_file = st.file_uploader("Choose an Excel file", type=["xlsx"])

if uploaded_file is not None:
    if st.button("Process File"):

        results = preprocess_file_calculation(uploaded_file)

        # Display the results using st.write()
        st.subheader("Results:")
        st.write(f"**Number of hours required:** {results['hours_required']}")
        st.write(f"**Number of hours worked:** {results['hours_worked']}")
        st.write(f"**Number of days worked:** {results['days_worked']}")
        avg_hour = int(results['total_hours_worked'] / results['days_worked'])
        avg_min = int(((results['total_hours_worked'] / results['days_worked']) - avg_hour) * 60)
        st.write(f"**Average hours worked per day:** {avg_hour}:{avg_min:02}")



        # Compare hours worked and hours required
        if results['total_hours_worked'] >= results['total_hours_required']:
            # Display "FULFILLED" in green
            st.markdown("<h1 style='text-align: center; color: green;'>FULFILLED</h1>", unsafe_allow_html=True)

            extra_hours_completed = int(results['total_hours_worked']-results['total_hours_required'])
            extra_minutes_completed = int(((results['total_hours_worked']-results['total_hours_required']) - extra_hours_completed ) * 60)
            # Display extra time fulfilled
            st.write(f"***Extra time fulfilled:*** {extra_hours_completed:02}:{extra_minutes_completed:02}")

            
            if results["days_until_15th"] > 0:
              
                hours_and_minutes_fulfilled = (extra_hours_completed*3600 + extra_minutes_completed*60 ) / results["days_until_15th"]
                hours_fulfilled = int(hours_and_minutes_fulfilled // 3600)
                minutes_fulfilled = int((hours_and_minutes_fulfilled % 3600) // 60)
                # Display extra time fulfilled per day
                st.write(f"***Time you can reduce per day and still meet goal:*** {hours_fulfilled:02}:{minutes_fulfilled:02}")

              
            else:
                # In the case the last day shown is on the 15th.
                st.write("***Unable to calculate time per day due to insufficient working days remaining***")



          
            df_merged = preprocess_table_display(uploaded_file)
            st.markdown(
            """
            <style>
            .streamlit-table {
                width: 1000px;  /* Adjust the width as needed */
            }
            </style>
            """,
            unsafe_allow_html=True)
          
            st.subheader("Work Hours Table")
            st.table(df_merged)  

        else:
            # Display "NOT FULFILLED" in red and calculate how much is left.
            st.markdown("<h1 style='text-align: center; color: red;'>NOT FULFILLED</h1>", unsafe_allow_html=True)
            hours_needed = int(results['total_hours_required']-results['total_hours_worked'])
            minutes_needed = int(((results['total_hours_required']-results['total_hours_worked']) - hours_needed ) * 60)
            st.write(f"***Total time required to fulfill goal:*** {hours_needed:02}:{minutes_needed:02}")


            if results["days_until_15th"] > 0:
              
                hours_and_minutes_to_complete = (hours_needed*3600 + minutes_needed*60 ) / results["days_until_15th"]
                hours_to_complete = int(hours_and_minutes_to_complete // 3600)
                minutes_to_complete = int((hours_and_minutes_to_complete % 3600) // 60)
                st.write(f"***Time required per day to fulfill goal:*** {hours_to_complete:02}:{minutes_to_complete:02}")
              
            else:
                st.write("***Unable to calculate time per day due to insufficient working days remaining***")


            
            df_merged = preprocess_table_display(uploaded_file)
            
            st.markdown(
            """
            <style>
            .streamlit-table {
                width: 1000px;  /* Adjust the width as needed */
            }
            </style>
            """,
            unsafe_allow_html=True)
          
            st.subheader("Work Hours Table")
            st.table(df_merged)  
          




