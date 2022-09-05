from datetime import datetime
from typing import List

import pandas as pd
import pymongo
import streamlit as st

from plots import TimelinePlot

# Set page name and icon
st.set_page_config(page_title="Ginny", page_icon="🌱")

url = f'mongodb+srv://{st.secrets["mongo"]["username"]}:{st.secrets["mongo"]["password"]}@plantbase.zb3enmb.mongodb.net/?retryWrites=true&w=majority'

# Initialize connection.
# Uses st.experimental_singleton to only run once.
@st.experimental_singleton
def init_connection():
    return pymongo.MongoClient(url)


client = init_connection()


def get_data():
    # Pull data from the collection.
    db = client.plantbase
    items = db.myplants.find()
    items = list(items)

    # Convert dates to datetime
    for item in items:
        item["dates_watered"] = sorted(
            pd.to_datetime(item["dates_watered"], infer_datetime_format=True)
        )
    return items


def register_new_plant(plant_name: str):
    db = client.plantbase
    # Default mark plant as watered on registered date
    doc = {
        "name": plant_name,
        "dates_watered": [datetime.now().strftime("%m/%d/%Y")],
        "dates_fertilized": [],
    }
    db.myplants.insert_one(doc)


def complete_action_by_date(
    plants_to_update: List[str], action_col: str, date_completed=datetime.now()
):
    # Log an action for a plant (e.g. water)
    db = client.plantbase
    for plant in plants_to_update:
        db.myplants.update_one(
            {"name": plant},
            {"$push": {action_col: date_completed.strftime("%m/%d/%Y")}},
        )


def format_days_since(days_since: int, prev_date: datetime):
    if days_since == 0:
        day_str = "Today"
    elif days_since == 1:
        day_str = "Yesterday"
    else:
        day_str = f"{days_since_water} days ago"
    return f"**{day_str}** - {prev_date.strftime('%b %d, %Y')}"


# Build application
st.markdown("# Plant tracker 🌱")

# Define actions in sidebar
selected_plants = []
with st.sidebar:
    st.markdown("# Actions")

    # Date input
    action_date = st.date_input("Set date")

    # New plant input
    new_plant_form = st.form(key="add_plant", clear_on_submit=True)
    new_plant_name = new_plant_form.text_input(
        label="Add plant 🌿", placeholder="New plant"
    )
    submitted = new_plant_form.form_submit_button(label="Add")
    if submitted:
        register_new_plant(new_plant_name)

    # Water action
    st.button(
        "Water 💦",
        on_click=complete_action_by_date,
        kwargs={
            "plants_to_update": selected_plants,
            "action_col": "dates_watered",
            "date_completed": action_date,
        },
    )

    # Fertilize action
    st.button(
        "Fertilize 🧪",
        on_click=complete_action_by_date,
        kwargs={
            "plants_to_update": selected_plants,
            "action_col": "dates_fertilized",
            "date_completed": action_date,
        },
    )


# Populate plants view
col1, col2 = st.columns(2)  # plant, last watered

col1.subheader("Plant")
col2.subheader("Last watered")

items = get_data()
# Sort items from least to most recently watered
items = [d for d in sorted(items, key=lambda i: i["dates_watered"][-1])]
for item in items:
    col1, col2 = st.columns(2)
    name = item["name"]
    last_watered_date = item["dates_watered"][-1]
    days_since_water = (datetime.now() - last_watered_date).days

    with col1:
        plant_select = st.checkbox(name)
        if plant_select:
            selected_plants.append(name)

    with col2:
        st.markdown(format_days_since(days_since_water, last_watered_date))


# Add plot under expander for mobile
st.markdown("## Data viz")
with st.expander("Display", expanded=False):
    tplot = TimelinePlot(items)
    st.pyplot(fig=tplot.get_fig())
