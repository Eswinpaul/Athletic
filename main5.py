import streamlit as st
import datetime
import pandas as pd
from docxtpl import DocxTemplate
from io import BytesIO
import zipfile
import os


st.set_page_config(page_title="CDMAA Referree Sheet Generator",page_icon=":sports_medal:",layout="wide")
st.title("Referee Sheet")
# st.markdown("---")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=['csv', 'xlsx'])

# Input fields for schedule time and date
cola, colb = st.columns(2)

with cola:
    schedule_time = st.time_input('Schedule Time')

with colb:
    date = st.date_input("Date", datetime.date.today())

# Arrange event, sub-event, age, and sex in a single row
col1, col2, col4, col3 = st.columns(4)

# Define sub-event options for each event
sub_events_dict = {
    "": [""],
    "Athletics": ["","100 M", "200 M", "400 M", "800 M", "1500 M", "5000 M", "10000 M", "80 M Hurdles", 
                  "100 M Hurdles", "110 M Hurdles", "200 M Hurdles", "300 M Hurdles", "400 M Hurdles", 
                  "5 Km Walk", "Long Jump", "High Jump", "Triple Jump", "Pole Vault", "Shot Put", 
                  "Discus Throw", "Javelin Throw", "Hammer Throw"],
    "Swimming": ["50 M Freestyle", "100 M Freestyle", "200 M Freestyle", "400 M Freestyle", 
                 "100 M Backstroke", "200 M Backstroke", "100 M Breaststroke", "200 M Breaststroke", 
                 "100 M Butterfly", "200 M Butterfly", "200 M Individual Medley", "400 M Individual Medley"]
}

age_group_restrictions = {
    "80 M Hurdles": {"Male": ["70+","75+","80+","85+","90+","95+","100+"], "Female": ["60+","65+","70+","75+","80+","85+","90+","95+","100+"]},
    "100 M Hurdles": {"Male": ["50+","55+","60+","65+"], "Female": ["40+", "45+", "50+","55+"]},
    "110 M Hurdles": {"Male": ["30+","35+","40+","45+"], "Female": ["30+", "35+"]},
    "200 M Hurdles": {"Male": ["80+","85+","90+","95+","100+"], "Female": ["70+", "75+","80+","85+","90+","95+","100+"]},
    "400 M Hurdles": {"Male": ["30+","35+","40+","45+"], "Female": ["30+", "35+"]},

    # Add other sub-events and their respective age group restrictions here
}

all_age_groups = ["All","30+", "35+", "40+", "45+", "50+", "55+", "60+", "65+", "70+", "75+", 
                               "80+", "85+", "90+",'95+', "100+"]


with col1:
    event = st.selectbox("Event", list(sub_events_dict.keys()), index=0)

with col2:
    sub_event_options = sub_events_dict.get(event, [""])
    sub_event = st.selectbox("Sub-Event",sub_event_options, index=0)
    
with col4:
    gender = st.selectbox("Gender", ["","All", "Male", "Female"], index=0)

with col3:
    age_groups = age_group_restrictions.get(sub_event, {"Male": all_age_groups, "Female": all_age_groups})
    # age = st.selectbox("Age Group", ["", "30+", "35+", "40+", "45+", "50+", "55+", "60+", "65+", "70+", "75+", 
    #                            "80+", "85+", "90+","95+", "100+"], index=0)
    age = st.selectbox("Age Group", age_groups.get(gender, all_age_groups))


data = None

if uploaded_file is not None:
    # Read the file based on its type
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
        st.info("File Uploaded Successfully!")
    elif uploaded_file.name.endswith('.xlsx'):
        data = pd.read_excel(uploaded_file)
        st.info("File Uploaded Successfully!")
else:
    st.info("Please upload a CSV or XLSX file.")


def get_other_events(row):
    events = [event for event in row[['Event 1', 'Event 2', 'Event 3']] if pd.notna(event) and event != sub_event and event != None]
    if not events:
            return ["Only 1 Event"]
    return events


def get_participants(data):
    participants = data[
    data[['Event 1', 'Event 2', 'Event 3']].apply(lambda x: sub_event in x.values, axis=1)
    ]
    if gender == "All":  
        if age == "All":
            participants = participants  # No filtering on Age Group or Sex
        else:
            participants = participants[participants['Age Group'] == age]  # Filter by Age Group
    else:
        if age == "All":
            participants = participants[participants['Sex'] == gender]  # Filter by Sex only
        else:
            participants = participants[
                (participants['Age Group'] == age) & (participants['Sex'] == gender)  # Filter by Age Group and Sex
            ]

        
    participants = participants.sort_values(by='full name')

    athletes = []
    for _, row in participants.iterrows():
        name = row['full name']
        chest_no = row['Chest_no']
        other_events = get_other_events(row)
        other_events_str = f"({', '.join(other_events)})"  # Format events as "(event1, event2)"
        athletes.append([chest_no,name, other_events_str])

    while len(athletes) < 10:
        athletes.append(["", "", ""])
          
    return athletes,participants  


athletes,parti = get_participants(data) if data is not None and not data.empty else (None, None)

if parti is not None and not parti.empty:
    selected = ['full name','Sex','Age Group','Chest_no','Birthday','Event 1','Event 2','Event 3']
    st.dataframe(parti[selected].reset_index(drop=True),use_container_width=True)

def chunk_athletes(athletes, chunk_size=15):
    chunks = []
    for i in range(0, len(athletes), chunk_size):
        chunk = athletes[i:i + chunk_size]
        # If the last chunk has fewer than 10 participants, fill the rest with empty entries
        while len(chunk) < chunk_size:
            chunk.append(["", "", ""])
        chunks.append(chunk)
    return chunks

if athletes:

    athlete_chunks = chunk_athletes(athletes)


# Template mapping
template_mapping = {
    "Long Jump": "long_jump_template.docx",
    "Triple Jump": "long_jump_template.docx",
    "Shot Put": "long_jump_template.docx",
    "Discus Throw": "long_jump_template.docx",
    "Javelin Throw": "long_jump_template.docx",
    "Hammer Throw": "long_jump_template.docx",
    "100 M": "sprint_template.docx",
    "200 M": "sprint_template.docx",
    "400 M": "sprint_template.docx",
    "800 M": "sprint_template.docx",
    "1500 M": "sprint_template.docx",
    "5000 M": "sprint_template.docx",
    "10000 M": "sprint_template.docx",
    "80 M Hurdles": "sprint_template.docx",
    "100 M Hurdles": "sprint_template.docx",
    "110 M Hurdles": "sprint_template.docx",
    "200 M Hurdles": "sprint_template.docx",
    "400 M Hurdles": "sprint_template.docx",
    "High Jump": "jumping_template.docx",
    "Pole Vault": "jumping_template.docx"
}

def create_zip_of_docx_files(athlete_chunks, schedule_time, date, event, sub_event, age, gender):
    zip_io = BytesIO()

    # Create a zip file in memory
    with zipfile.ZipFile(zip_io, 'w', zipfile.ZIP_DEFLATED) as zipf:
        try:
            # Loop through athlete chunks to generate files
            for idx, data in enumerate(athlete_chunks):
                selected_template = template_mapping.get(sub_event)
                if selected_template:
                    selected_values = {
                        "t": schedule_time.strftime("%H:%M"),
                        "date": date.strftime("%d-%m-%Y"),
                        "cat": event if event else None,
                        "event_name_list": sub_event if sub_event else None,
                        "age": age if age else None,
                        "sex": gender if gender else None,
                        # "sno": "S.NO", "chest": "CHEST NO", "name": "NAME", "dist": "DISTRICT", "timing": "TIMING", "place": "PLACE",
                        "athletes": data
                    }
                    
                    # Generate docx file in memory
                    docx_filename = f"referee_sheet_{event}_{sub_event}_{age}_{gender}_{idx+1}.docx"
                    docx_io = BytesIO()

                    doc = DocxTemplate(selected_template)
                    doc.render(selected_values)
                    doc.save(docx_io)
                    docx_io.seek(0)

                    # Write the docx file to the zip
                    zipf.writestr(docx_filename, docx_io.read())

        except Exception as e:
            st.error(f"An error occurred while generating the zip file: {e}")
            return None

    # Seek to the beginning of the zip file to prepare for download
    zip_io.seek(0)

    return zip_io

# Update the button logic for downloading all files
colc, cold = st.columns(2)

if colc.button("Generate All Files"):
    # Check if all required fields are filled
    fields_filled = all([event, sub_event, age, gender, date, schedule_time])

    if fields_filled:
        selected_template = template_mapping.get(sub_event)
        if selected_template:
            try:
                # Generate the zip file containing all docx files
                zip_io = create_zip_of_docx_files(athlete_chunks, schedule_time, date, event, sub_event, age, gender)

                if zip_io:
                    # Create a download button for the zip file
                    st.download_button(
                        label="Download All Referee Sheets",
                        data=zip_io,
                        file_name="all_referee_sheets.zip",
                        mime="application/zip"
                    )

            except Exception as e:
                st.error(f"An error occurred: {e}")
        else:
            st.warning("No template found for the selected sub-event.")
    else:
        st.warning("Please fill out all required fields to generate the document.")
