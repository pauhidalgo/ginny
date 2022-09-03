import streamlit as st
import pymongo
import pandas as pd

url = f'mongodb+srv://{st.secrets["mongo"]["username"]}:{st.secrets["mongo"]["password"]}@plantbase.zb3enmb.mongodb.net/?retryWrites=true&w=majority'
data_path = "C:\\Users\\hidal\\Downloads\\plant watering data - data.csv"

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(url)


client = init_connection()

db = client.plantbase
coll = db.myplants

data = pd.read_csv(data_path)
docs = []
for column in data.columns:
    docs.append(
        {
            "name": column,
            "dates_watered": data[column].dropna().tolist(),
            "dates_fertilized": [],
        }
    )

db.myplants.delete_many({})
result = coll.insert_many(docs)

client.close()
