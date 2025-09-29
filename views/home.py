import streamlit as st 
import pandas as pd

st.title("🏅 ATHLETIC MEET")
# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv','XLSX'])
# uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx"])

age_groups = {
    '30+': ('1990-02-23', '1995-02-22'),'35+': ('1985-02-23', '1990-02-22'),
    '40+': ('1980-02-23', '1985-02-22'),'45+': ('1975-02-23', '1980-02-22'),
    '50+': ('1970-02-23', '1975-02-22'),'55+': ('1965-02-23', '1970-02-22'),
    '60+': ('1960-02-23', '1965-02-22'),'65+': ('1955-02-23', '1960-02-22'),
    '70+': ('1950-02-23', '1955-02-22'),'75+': ('1945-02-23', '1950-02-22'),
    '80+': ('1940-02-23', '1945-02-22'),'85+': ('1935-02-23', '1940-02-22'),
    '90+': ('1930-02-23', '1935-02-22'),'95+': ('1925-02-23', '1930-02-22'),
    '100+': ('1920-02-23', '1925-02-22')
}

def get_age_group(birthday):
    if pd.isnull(birthday):  # Handle NaT values
        return None
    for group, (start_date, end_date) in age_groups.items():
        if pd.to_datetime(start_date) <= birthday <= pd.to_datetime(end_date):
            return group
    return '0'

def process_data(data):
    data[['Event 1', 'Event 2', 'Event 3']] = data[['Event 1', 'Event 2', 'Event 3']].apply(lambda col: col.map(lambda x: x.title() if isinstance(x, str) else x))
    data['Age Group'] = data['Birthday'].apply(get_age_group)
    data["Mobile Number"] = data["Mobile Number"].apply(lambda x: str(int(x)) if pd.notnull(x) else "")
    data['Emergency Contact  Mobile no'] = data['Emergency Contact  Mobile no'].apply(lambda x: str(int(x)) if pd.notnull(x) else "")
    event_columns = ['Event 1', 'Event 2', 'Event 3']
    data[event_columns] = data[event_columns].apply(lambda col: col.str.replace(r'\s*\(.*?\)\s*', '', regex=True))


def assign_chest_no(group):
    group = group.sort_values(by="full name").reset_index(drop=True)
    age_prefix = int(group['Age Group'].iloc[0].split('+')[0]) * 100  # e.g., 30+ -> 3000
    group['Chest_no'] = [age_prefix + i for i in range(1, len(group) + 1)]

    return group

if "my_data" not in st.session_state:
    st.session_state["my_data"] = ""

if uploaded_file is not None:
    # Read the file based on its type
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
        st.info("File Uploaded Successfully!")
    else:
        d = pd.ExcelFile(uploaded_file) 
        Data = pd.read_excel(d,sheet_name = "Form responses 1")
        data = Data[['Name (Fill the name in Capital Letters ) ', 'Second part of name/Initial(s)/ Second Name ' ,'Date of Birth', 'Mobile Number','Email address','Sex', 'Blood Group','Emergency Contact  Mobile no','Address','Age (As on 25.02.2026)',
                    'Event 1', 'Event 2', 'Event 3']].copy()
        # data['Member Status'] = Data.iloc[:, 22].fillna(Data.iloc[:, 34])
        data['Member Status'] = data['Member Status'].str.lower().apply(lambda x: 'New' if 'New member' in x else 'Old')
        data['Member Status'] = (
    data['Member Status']
    .fillna('')  # Convert NaN to an empty string
    .str.lower()
    .apply(lambda x: 'New' if 'New member' in x else 'Old')
)
        data.rename(columns={'Date of Birth': 'Date Of Birth','Sex':'Sex'}, inplace=True)

        # Convert '7. Date of Birth' to datetime format
        data['Birthday'] = pd.to_datetime(data['Date Of Birth'], errors='coerce')
        data['full name'] = data['Name (Fill the name in Capital Letters )'].str.cat(data['Second part of name/Initial(s)/ Second Name'], sep=' ')

        st.info("File Uploaded Successfully!")
        st.subheader("Select the filters")
        st.markdown("Use the filters below to preprocess the data as per your requirements.")
        col_1, col_2 = st.columns(2,gap='small',vertical_alignment='center')

        with col_1:
            age_grouped = st.checkbox("Group by Age")

        with col_2:
            generate_chest_no = st.checkbox("Generate Chest No")

        if age_grouped:
            process_data(data)    
            
        if generate_chest_no:
            # Apply the function to each age group and save the result
            data = data.groupby('Age Group', group_keys=False).apply(assign_chest_no)
            data['Chest_no'] = data['Chest_no'].astype(str)
            data['Date Of Birth'] = data['Date Of Birth'].dt.strftime('%d-%m-%Y')
            data.drop(columns=['Birthday','Name','Initial(s) (can use space)'], inplace=True)
            data = data.reset_index(drop=True)    #############
            data = data[['Chest_no','full name','Date Of Birth', 'Age Group','Mobile Number','Email address','Sex', 'Blood Group ','Emergency Contact  Mobile no','Address ','Age (As on 22.02.2025)',
                    'Event 1', 'Event 2', 'Event 3','Member Status']].copy()
            
            
        filter = st.button("Apply Filters")

        if filter and uploaded_file is not None:
            data.index = data.index + 1
            st.dataframe(data)

        if age_grouped and generate_chest_no:
            if uploaded_file is None:
                st.error("Please upload a file to proceed.")
            else:
                st.success("Filters applied. File uploaded successfully!")
        # Proceed with further processing
        else:
            st.info("Please apply filters and then proceed.")
    st.session_state["my_data"] = data        
          
else:
    st.info("Please upload a CSV or XLSX file.")






