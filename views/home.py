import streamlit as st 
import pandas as pd

st.title("🏅 ATHLETIC MEET")
# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv','XLSX'])
# uploaded_file = st.sidebar.file_uploader("Upload a file", type=["csv", "xlsx"])

age_groups = {
    '30+': ('1991-02-25', '1996-02-26'),'35+': ('1986-02-25', '1991-02-26'),
    '40+': ('1981-02-25', '1986-02-26'),'45+': ('1976-02-25', '1981-02-26'),
    '50+': ('1971-02-25', '1976-02-26'),'55+': ('1966-02-25', '1971-02-26'),
    '60+': ('1961-02-25', '1966-02-26'),'65+': ('1956-02-25', '1961-02-26'),
    '70+': ('1951-02-25', '1956-02-26'),'75+': ('1946-02-25', '1951-02-26'),
    '80+': ('1941-02-25', '1946-02-26'),'85+': ('1936-02-25', '1941-02-26'),
    '90+': ('1931-02-25', '1936-02-26'),'95+': ('1926-02-25', '1931-02-26'),
    '100+': ('1921-02-25', '1926-02-26')
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
    # data['Emergency Contact  Mobile no'] = data['Emergency Contact  Mobile no'].apply(lambda x: str(int(x)) if pd.notnull(x) else "")
    data['Emergency Contact  Mobile no'] = data['Emergency Contact  Mobile no'].apply(
    lambda x: re.sub(r'\D', '', str(x))[-10:] if pd.notnull(x) and len(re.sub(r'\D', '', str(x))) >= 10 else ""
)
    event_columns = ['Event 1', 'Event 2', 'Event 3']
    data[event_columns] = data[event_columns].apply(lambda col: col.str.replace(r'\s*\(.*?\)\s*', '', regex=True))


# def assign_chest_no(group):
#     group = group.sort_values(by="full name").reset_index(drop=True)
#     age_prefix = int(group['Age Group'].iloc[0].split('+')[0]) * 100  # e.g., 30+ -> 3000
#     group['Chest_no'] = [age_prefix + i for i in range(1, len(group) + 1)]

#     return group
def assign_chest_no(data):
    # First, sort by Age Group, Sex, and full name alphabetically
    data = data.sort_values(by=['Age Group', 'Sex', 'full name']).reset_index(drop=True)

    # Function to assign chest numbers within each Age Group + Sex subgroup
    def chest_number_subgroup(group):
        # Get age prefix from 'Age Group', e.g., 30+ -> 3000
        age_prefix = int(group['Age Group'].iloc[0].split('+')[0]) * 100
        # Assign chest numbers starting from age_prefix + 1
        group['Chest_no'] = [age_prefix + i for i in range(1, len(group) + 1)]
        return group

    # Group by Age Group and Sex, then apply chest number assignment
    data = data.groupby(['Age Group', 'Sex'], group_keys=False).apply(chest_number_subgroup)

    return data


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
        Data.columns = [str(c).strip() for c in Data.columns]
        required_cols = [
    'Name (Fill the name in Capital Letters )',
    'Second part of name/Initial(s)/ Second Name',
    'Date of Birth',
    'Mobile Number',
    'Email address',
    'Sex',
    'Blood Group',
    'Emergency Contact  Mobile no',
    'Address',
    'Age (As on 25.02.2026)',
    'Event 1',
    'Event 2',
    'Event 3',
    'Member Confirmation'
]

# Select only the columns that exist in the DataFrame (optional safeguard)
        existing_cols = [c for c in required_cols if c in Data.columns]

# Make a copy for processing
        data = Data[existing_cols].copy()
        # data = Data[['Name (Fill the name in Capital Letters )', 'Second part of name/Initial(s)/ Second Name' ,'Date of Birth', 'Mobile Number','Email address','Sex', 'Blood Group','Emergency Contact  Mobile no','Address','Age (As on 25.02.2026)','Event 1', 'Event 2', 'Event 3','Member Confirmation']].copy()
        data['Member Status'] = Data['Member Confirmation'].str.lower().apply(lambda x: 'New' if 'new member' in x else 'Old')
        # data['Member Status'] = (
#     data['Member Status']
#     .fillna('')  # Convert NaN to an empty string
#     .str.lower()
#     .apply(lambda x: 'New' if 'New member' in x else 'Old')
# )
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
            data.drop(columns=['Birthday','Name (Fill the name in Capital Letters )','Second part of name/Initial(s)/ Second Name'], inplace=True)
            data = data.reset_index(drop=True)    #############
            data = data[['Chest_no','full name','Date Of Birth', 'Age Group','Mobile Number','Email address','Sex', 'Blood Group','Emergency Contact  Mobile no','Address','Age (As on 25.02.2026)',
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


















