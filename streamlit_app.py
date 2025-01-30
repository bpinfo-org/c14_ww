import streamlit as st
import os
import tempfile
import time

from ward_and_wilson_test import read_dates, save_std_out, generate_output, run


st.set_page_config(page_title='c14 - Ward and Wilson Test')

# Create a container for the logo with a fixed height of 200 pixels
with st.container():
    st.image("c14-logo.png", width=150)  # Adjust the path if necessary

# Streamlit interface
st.title("Ward and Wilson Test")

# Add a download button for the example dataset
st.download_button(
    label="Download example dataset",
    data=open('dataset.csv', 'rb').read(),
    file_name='dataset.csv',
    mime='text/csv'
)

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Text input for dataset only if no file is uploaded
if uploaded_file is None:
    dataset_input = st.text_area("Enter your dataset (CSV format)", height=200)
else:
    dataset_input = None  # No text input if a file is uploaded

# Confidence level input
confidence_level = st.number_input("Confidence Level (0-100)", min_value=0, max_value=100, value=0)


if st.button("Run Analysis"):
    if uploaded_file is not None:
        # Save the uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(uploaded_file.getbuffer())
            dataset_file = temp_file.name  # Use the temporary file for analysis
    elif dataset_input:
        # Create a temporary file for the text input
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file.write(dataset_input.encode('utf-8'))  # Write the string input to the temp file
            dataset_file = temp_file.name  # Use the temporary file for analysis
    else:
        st.error("Please upload a file or enter a dataset in CSV format.")
        dataset_file = None

    if dataset_file:
        # Run the analysis
        output_folder = os.getcwd()  # You can change this to a specific folder if needed
        try:
            start_time = time.time()
            run(dataset_file=dataset_file, output_folder=output_folder, confidence_level=confidence_level)
            end_time = time.time()

            # Display results
            results_file = os.path.join(output_folder, 'results.txt')
            with open(results_file, 'r') as f:
                results = f.read()

            st.success("Analysis completed!")
            st.text_area("Results", results, height=300)

            st.write(f"Script runtime: {end_time - start_time:.2f} seconds")

        except Exception as e:
            st.error(f"An error occurred: {e}")


# Clean up the temporary file if needed
if os.path.exists("temp_dataset.csv"):
    os.remove("temp_dataset.csv")
