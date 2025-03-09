import streamlit as st
import pandas as pd

# Connect to Snowflake using st.experimental_connection()
conn = st.experimental_connection("snowflake", type="snowflake")

# Function to fetch data from Snowflake
def fetch_data():
    query = "SELECT * FROM ANIMALS"
    df = conn.query(query, ttl=600)  # Cache for 10 minutes
    return df

# Function to update a row
def update_row(row_id, name, species, age, colour, description):
    update_query = f"""
    UPDATE ANIMALS 
    SET NAME = '{name}', SPECIES = '{species}', AGE = {age}, COLOUR = '{colour}', DESCRIPTION = '{description}'
    WHERE ID = {row_id}
    """
    conn.execute(update_query)
    st.success(f"Updated ID {row_id} successfully!")

# Function to add a new row
def add_new_animal(name, species, age, colour, description):
    insert_query = f"""
    INSERT INTO ANIMALS (NAME, SPECIES, AGE, COLOUR, DESCRIPTION)
    VALUES ('{name}', '{species}', {age}, '{colour}', '{description}')
    """
    conn.execute(insert_query)
    st.success("New animal added successfully!")

# Fetch data from Snowflake
st.title("🐾 Animal Database (Snowflake)")

df = fetch_data()

# ✅ Search Feature
search = st.text_input("🔍 Search by Name, Species, or Colour").lower()
if search:
    df = df[df.apply(lambda row: search in str(row["NAME"]).lower() or 
                               search in str(row["SPECIES"]).lower() or 
                               search in str(row["COLOUR"]).lower(), axis=1)]

# ✅ Editable Data Table
st.subheader("📋 Edit Animal Records")
edited_df = st.data_editor(df, key="editable_table", num_rows="dynamic")

# ✅ Update Edited Rows
if st.button("💾 Save Changes"):
    for i, row in edited_df.iterrows():
        update_row(row["ID"], row["NAME"], row["SPECIES"], row["AGE"], row["COLOUR"], row["DESCRIPTION"])
    st.experimental_rerun()

# ✅ Add New Animal
st.subheader("➕ Add a New Animal")
with st.form("new_animal_form"):
    new_name = st.text_input("Name")
    new_species = st.text_input("Species")
    new_age = st.number_input("Age", min_value=0)
    new_colour = st.text_input("Colour")
    new_description = st.text_area("Description")

    submit_button = st.form_submit_button("Add Animal")
    if submit_button:
        add_new_animal(new_name, new_species, new_age, new_colour, new_description)
        st.experimental_rerun()