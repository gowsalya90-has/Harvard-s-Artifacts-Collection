import sys
import streamlit as st
st.title("🏛️ HARVARD'S ARTIFACTS COLLECTION")
import streamlit as st
import pymysql
import pandas as pd
import random
import requests

API_KEY = "d6eb908a-e375-4aa7-a997-db5cc795535d"

metadata = []
media = []
colors = []

# --------- MySQL Connection ---------
def get_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="G0w$1@123",
        database="harvards_db",
        cursorclass=pymysql.cursors.DictCursor
    )

# --------- Simulated API Fetch Function ---------
# --- Get Classifications from API ---
def get_classifications():
    url = "https://api.harvardartmuseums.org/classification"
    params = {"apikey": API_KEY, "size": 100}
    response = requests.get(url, params=params)
    return [item['name'] for item in response.json().get("records", [])]

# --- Fetch Object Data by Classification ---
def fetch_objects(classification, min_records=2500):
    page = 1
    collected = []
    while len(collected) < min_records:
        url = "https://api.harvardartmuseums.org/object"
        params = {
            "classification": classification,
            "size": 100,
            "page": page,
            "apikey": API_KEY
        }
        response = requests.get(url, params=params)
        data = response.json()
        records = data.get("records", [])
        if not records:
            break
        collected.extend(records)
        page += 1
    return collected[:min_records]

# --- Parse records ---
def parse_records(records):
    meta, med, clr = [], [], []
    for i in records:
        meta.append(dict(
            id=i.get('id'),
            title=i.get('title'),
            culture=i.get('culture'),
            period=i.get('period'),
            century=i.get('century'),
            medium=i.get('medium'),
            dimensions=i.get('dimensions'),
            description=i.get('description'),
            department=i.get('department'),
            classification=i.get('classification'),
            accessionyear=i.get('accessionyear'),
            accessionmethod=i.get('accessionmethod'),
        ))
        med.append(dict(
            objid=i.get('objectid'),
            imgcount=i.get('imagecount'),
            medcount=i.get('mediacount'),
            clrcount=i.get('colorcount'),
            rank=i.get('rank'),
            dtbrgin=i.get('datebegin'),
            dtend=i.get('dateend'),
        ))
        for c in i.get("colors", []):
            clr.append(dict(
                objid=i.get('objectid'),
                color=c.get('color'),
                spectrum=c.get('spectrum'),
                hue=c.get('hue'),
                percent=c.get('percent'),
                css3=c.get('css3'),
            ))
    return meta, med, clr

# --- Insert data into MySQL ---
def insert_into_db(meta, med, clr):
    conn = get_connection()
    cursor = conn.cursor()

    # Metadata
    sql_meta = """
        INSERT IGNORE INTO artifact_metadata
        (id, title, culture, period, century, medium, dimensions, description, department, classification, accessionyear, accessionmethod)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """
    for item in meta:
        cursor.execute(sql_meta, tuple(item.values()))

    # Media
    sql_media = """
        INSERT IGNORE INTO artifact_media
        (objectid, imagecount, mediacount, colorcount, `rank`, datebegin, dateend)
        VALUES (%s, %s, %s, %s, %s, %s, %s)
    """
    for item in med:
        cursor.execute(sql_media, tuple(item.values()))

    # Colors
    sql_colors = """
        INSERT INTO artifact_colors
        (objectid, color, spectrum, hue, percent, css3)
        VALUES (%s, %s, %s, %s, %s, %s)
    """
    for item in clr:
        cursor.execute(sql_colors, tuple(item.values()))

    conn.commit()
    cursor.close()
    conn.close()

# --------- App UI ---------
st.set_page_config(page_title="Artifact Data Explorer", layout="wide")
classification = st.selectbox(
    "Select Artifact Classification",
    ["Coins", "Vessels", "Drawings", "Prints", "Photographs"]
)

col1, col2, col3 = st.columns(3)
if 'fetched_data' not in st.session_state:
    st.session_state['fetched_data'] = []

# --------- Buttons ---------
with col1:
    if st.button("🔄 Collect Data"):
        with st.spinner("Fetching data from Harvard Art Museum API..."):
            records = fetch_objects(classification, min_records=2500)
            meta, med, clr = parse_records(records)
            st.session_state.metadata = meta
            st.session_state.media = med
            st.session_state.colors = clr
            st.success(f"✅ Fetched {len(meta)} metadata records.")

with col2:
    import streamlit as st
import pandas as pd

# Dummy data for testing
if "metadata" not in st.session_state:
    st.session_state.metadata = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
    st.session_state.media = [{"file": "image1.png"}, {"file": "image2.png"}]
    st.session_state.colors = [{"color": "#FF5733"}, {"color": "#33C3FF"}]

# Button
if st.button("👁 Show Data"):
    st.markdown("---")  # Divider

    with st.expander("🗃 Metadata", expanded=True):
        metadata = st.session_state.get("metadata", [])
        if metadata:
            st.dataframe(pd.DataFrame(metadata), use_container_width=True)
        else:
            st.info("No metadata available.")

    st.markdown(" ")

    with st.expander("🖼 Media", expanded=True):
        media = st.session_state.get("media", [])
        if media:
            st.dataframe(pd.DataFrame(media), use_container_width=True)
        else:
            st.info("No media data available.")

    st.markdown(" ")

    with st.expander("🎨 Colors", expanded=True):
        colors = st.session_state.get("colors", [])
        if colors:
            st.dataframe(pd.DataFrame(colors), use_container_width=True)
        else:
            st.info("No color data available.")

    st.markdown("---")


with col3:
    if st.button("💾 Insert into SQL"):
        with st.spinner("Inserting into MySQL..."):
            insert_into_db(
                st.session_state.metadata,
                st.session_state.media,
                st.session_state.colors
            )
            st.success("✅ All data inserted into MySQL database.")

# --- Query & Visualization Section ---
st.markdown("---")
st.subheader("📊 SQL Queries & Outputs")

query_options = {
        "List all artifacts from the 11th century belonging to Byzantine culture": "SELECT * FROM artifact_metadata WHERE culture = 'Byzantine' and century = '11th century'",
    "What are the unique cultures represented in the artifacts":"SELECT DISTINCT culture FROM artifact_metadata",
    "List all artifacts from the Archaic Period":"SELECT * FROM artifact_metadata WHERE period = 'Archaic period'",
    "List artifact titles ordered by accession year in descending order":"SELECT title,accessionyear FROM artifact_metadata ORDER BY accessionyear DESC",
    "How many artifacts are there per department":"SELECT department, count(*) as 'count of artifacts' FROM artifact_metadata GROUP BY department",
    "Which artifacts have more than 1 image":"SELECT * FROM artifact_media WHERE imagecount > 1",
    "What is the average rank of all artifacts":"SELECT avg(`rank`) FROM artifact_media",
    "Which artifacts have a higher colorcount than mediacount":"SELECT * FROM artifact_media where colorcount > mediacount",
    "List all artifacts created between 1500 and 1600":"SELECT * FROM artifact_media where datebegin between 1500 and 1600",
    "How many artifacts have no media files":"SELECT count(*) as 'Count of Artifacts have no media files' FROM artifact_media WHERE mediacount = 0",
    "What are all the distinct hues used in the dataset": "SELECT distinct hue from artifact_colors",
    "What are the top 5 most used colors by frequency?": "SELECT color, COUNT(*) AS frequency FROM artifact_colors GROUP BY color ORDER BY frequency DESC LIMIT 5",
    "What is the average coverage percentage for each hue?":"select hue,avg(percent) from  artifact_colors group by hue",
    "List all colors used for a given artifact ID.":"select  color from artifact_colors where objectid = 1412",
    "What is the total number of color entries in the dataset?":"select color,count(color) from artifact_colors group by color",
    "List artifact titles and hues for all artifacts belonging to the Byzantine culture?":"select title,hue from artifact_metadata inner join artifact_colors on id = objectid where culture = 'Byzantine'",
    "List each artifact title with its associated hues.":"SELECT title, hue FROM artifact_metadata INNER JOIN artifact_colors ON id = objectid;",
    "Get artifact titles, cultures, and media ranks where the period is not null":"select title,culture,mediacount,`rank` from artifact_metadata inner join  artifact_media on id = objectid where period is not null",
    "Find artifact titles ranked in the top 10 that include the color hue Grey":"select distinct met.title,`rank` from artifact_metadata as met inner join artifact_colors as col on met.id =  col.objectid inner join artifact_media as med on med.objectid = met.id where col.hue = 'grey' ORDER BY `rank` desc LIMIT 10",
    "How many artifacts exist per classification, and what is the average media count for each?":"SELECT classification,count(*) AS artifact_count,AVG(mediacount) AS avg_media_count FROM artifact_metadata inner join  artifact_media on id = objectid GROUP BY classification"

}

selected_query = st.selectbox("Choose a query", list(query_options.keys())) 

if st.button("📥 Run Given Query"):
    query = query_options[selected_query]
    with get_connection().cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        df_query = pd.DataFrame(result)
        st.dataframe(df_query, use_container_width=True)

st.markdown("---")
st.subheader("📊 Own Queries & Outputs")
query_options = {"All Metadata": "SELECT * FROM artifact_metadata",
    "All Media": "SELECT * FROM artifact_media",
    "All Colors": "SELECT * FROM artifact_colors",
    "Find the classification with more artifacts": "SELECT classification,count(*) as 'Number of artifiacts' FROM artifact_metadata group by classification order by count(*) desc LIMIT 1",
    "Find the number of artifacts in each century": "SELECT century,count(*) as 'Number of artifiacts' FROM artifact_metadata group by century order by count(*) desc",
    "Find the highest and lowest rank": "SELECT MAX(`rank`) as 'Highest Rank',min(`rank`) as 'Lowest Rank' FROM artifact_media",
    "Find the Lowest datebegin": "SELECT Min(datebegin) as 'Lowest Date' FROM artifact_media"}

selected_query = st.selectbox("Choose a query", list(query_options.keys())) 

if st.button("📥 Run Own Query"):
    query = query_options[selected_query]
    with get_connection().cursor() as cursor:
        cursor.execute(query)
        result = cursor.fetchall()
        df_query = pd.DataFrame(result)
        st.dataframe(df_query, use_container_width=True)