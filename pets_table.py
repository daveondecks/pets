import streamlit as st
import pandas as pd
import snowflake.connector

# ✅ Load Snowflake credentials securely from Streamlit Secrets
snowflake_secrets = st.secrets["connections.snowflake"]

# ✅ Connect to Snowflake manually
def get_snowflake_connection():
    return snowflake.connector.connect(
        user=snowflake_secrets["user"],
        password=snowflake_secrets["password"],
        account=snowflake_secrets["account"],
        warehouse=snowflake_secrets["warehouse"],
        database=snowflake_secrets["database"],
        schema=snowflake_secrets["schema"]
    )

# ✅ Function to Fetch Data from Snowflake
def fetch_data():
    conn = get_snowflake_connection()
    query = "SELECT * FROM ANIMALS"
    df = pd.read_sql(query, conn)
    conn.close()
    return df

# ✅ Function to Update an Existing Row
def update_row(row_id, name, species, age, colour, description):
    conn = get_snowflake_connection()
    update_query = f"""
    UPDATE ANIMALS 
    SET NAME = '{name}', SPECIES = '{species}', AGE = {age}, COLOUR = '{colour}', DESCRIPTION = '{description}'
    WHERE ID = {row_id}
    """
    cur = conn.cursor()
    cur.execute(update_query)
    conn.commit()
    conn.close()
    st.success(f"Updated ID {row_id} successfully!")

# ✅ Function to Add a New Row
def add_new_animal(name, species, age, colour, description):
    conn = get_snowflake_connection()
    insert_query = f"""
    INSERT INTO ANIMALS (NAME, SPECIES, AGE, COLOUR, DESCRIPTION)
    VALUES ('{name}', '{species}', {age}, '{colour}', '{description}')
    """
    cur = conn.cursor()
    cur.execute(insert_query)
    conn.commit()
    conn.close()
    st.success("New animal added successfully!")

# 🔹 Fetch Data from Snowflake
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