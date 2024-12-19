import pandas as pd
import streamlit as st

# Streamlit App
st.title("Remove Duplicate Rows Across Files")

# File Uploader
refrence_file = st.file_uploader("Upload CSV reference file", accept_multiple_files=False, type=["csv"])
uploaded_files = st.file_uploader("Upload CSV files", accept_multiple_files=True, type=["csv"])

if refrence_file:
    appmedlow_data = None
    df = pd.read_csv(refrence_file)
    file_key = refrence_file.name  # Use file name as the key
    appmedlow_data = df

if uploaded_files:
    data = {}  # Dictionary to store data from files

    # Read all uploaded files into pandas dataframes
    for uploaded_file in uploaded_files:
        try:
            # Read the uploaded CSV file
            df = pd.read_csv(uploaded_file)
            file_key = uploaded_file.name  # Use file name as the key
            data[file_key] = df  # Store the entire dataframe

        except Exception as e:
            st.error(f"Error processing file {uploaded_file.name}: {e}")

    # Process the data if there are valid files
    if data and appmedlow_data is not None:
        # Combine all files into one (excluding AppMedLow)
        other_data = pd.concat([df for file_name, df in data.items()])

        # Find duplicate rows in other files that are present in AppMedLow
        duplicate_rows = appmedlow_data.merge(other_data, how="inner", indicator=True)

        # Now we need to remove these duplicate rows from all files except AppMedLow
        deleted_data = {}  # To store deleted rows' samples
        file_counts = {}  # Dictionary to store row counts before and after

        for file_name, df in data.items():
            # Get the initial count of rows
            initial_row_count = len(df)

            # Remove rows that are identical to rows in AppMedLow (duplicates)
            df_cleaned = df.merge(duplicate_rows, how="left", indicator="merge_status").query('merge_status == "left_only"').drop(columns=['merge_status'])
            
            # Track the deleted rows (those which were removed)
            deleted_rows = df[~df.index.isin(df_cleaned.index)]
            deleted_data[file_name] = deleted_rows

            # Get the final count of rows after removing duplicates
            final_row_count = len(df_cleaned)
        
            # Store the row counts before and after
            file_counts[file_name] = {"initial": initial_row_count, "final": final_row_count}

        # Display the row counts before and after and provide a sample of deleted rows
        for file_name, file_data in deleted_data.items():
            st.write(f"**{file_name}:**")
            st.write(f"Rows before removing duplicates: {file_counts[file_name]['initial']}")
            st.write(f"Rows after removing duplicates: {file_counts[file_name]['final']}")

            # Display a sample of the deleted rows with the row index + 2
            if not file_data.empty:
                deleted_data_sample = file_data.head()  # Get the first 5 deleted rows as a sample
                deleted_data_sample.index = deleted_data_sample.index + 2  # Adjust index by +2
                st.write(f"Sample of deleted rows from {file_name}:")
                st.write(deleted_data_sample)

            else:
                st.write(f"No rows were deleted from {file_name}.")

    else:
        st.warning("No valid data found in the uploaded files or missing 'AppMedLow.csv'.")