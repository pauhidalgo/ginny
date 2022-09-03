from time import strptime
import streamlit as st
import pymongo
from datetime import datetime

url = f'mongodb+srv://{st.secrets["mongo"]["username"]}:{st.secrets["mongo"]["password"]}@plantbase.zb3enmb.mongodb.net/?retryWrites=true&w=majority'

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(url)


client = init_connection()

# Pull data from the collection.
# Uses st.experimental_memo to only rerun when the query changes or after 10 min.
@st.experimental_memo(ttl=600)
def get_data():
    db = client.plantbase
    items = db.myplants.find()
    items = list(items)  # make hashable for st.experimental_memo
    return items


items = get_data()

# Format application
st.markdown("# Plant tracker :seedling:")

st.date_input("Current date")

col1, col2, col3 = st.columns(3) # plant, days since water
selected_plants = []

col1.subheader("Plant")
col2.subheader("Last watered")
col3.subheader("Actions")

col3.button("Water")
col3.button("Fertilize")

for item in items: 
    name = item['name']
    last_watered = datetime.strptime(item['dates_watered'][-1], '%m/%d/%Y')
    days_since_water = (datetime.now() - last_watered).days

    with col1: 
        plant_select = st.checkbox(name)
        if plant_select: 
            selected_plants.append(name)
    
    with col2: 
        st.write(f"{days_since_water} days ago - {last_watered.strftime('%b %d, %Y')}")
    

st.write(selected_plants)


