import pandas as pd
import streamlit as st
from gsheetsdb import connect

# Create a connection object.
conn = connect()

# Perform SQL query on the Google Sheet.
# Uses st.cache to only rerun when the query changes or after 10 min.
@st.cache(ttl=600)
def run_query(query):
    rows = conn.execute(query, headers=1)
    df = pd.DataFrame(rows.fetchall())
    df.columns=[x[0] for x in rows.description]
    return df

sheet_url = st.secrets["public_gsheets_url"]
df = run_query(f'SELECT * FROM "{sheet_url}"')

# Display result df
st.dataframe(data=df)
