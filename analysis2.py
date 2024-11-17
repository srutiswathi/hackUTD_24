import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler, LabelEncoder
from fpdf import FPDF
import streamlit as st
import requests
import io
import os


# Upload PDF to Pinata
def upload_to_pinata(file_path, pinata_api_key, pinata_secret_api_key):
    """
    Upload a file to Pinata and return the response.
    :param file_path: Path to the file to upload.
    :param pinata_api_key: API key for Pinata.
    :param pinata_secret_api_key: Secret API key for Pinata.
    :return: Pinata response as a dictionary.
    """
    if not pinata_api_key or not pinata_secret_api_key:
        raise ValueError("Pinata API key and Secret key must be provided and non-empty strings.")

    # Debug keys
    print(f"API Key: {repr(pinata_api_key)}")
    print(f"Secret Key: {repr(pinata_secret_api_key)}")

    url = "https://api.pinata.cloud/pinning/pinFileToIPFS"
    headers = {
        "pinata_api_key": pinata_api_key,
        "pinata_secret_api_key": pinata_secret_api_key
    }

    if not os.path.exists(file_path):
        raise FileNotFoundError(f"The file {file_path} does not exist.")

    try:
        with open(file_path, "rb") as file:
            files = {"file": file}
            response = requests.post(url, files=files, headers=headers)
            print(f"Response Status: {response.status_code}")
            print(f"Response JSON: {response.json()}")
            return response.json()
    except Exception as e:
        print(f"Error during upload: {e}")
        return {"error": str(e)}

def analysis_page():
    # Title and description
    st.title("🚗 Vehicle Fuel Economy Analysis (2021–2025)")
    st.markdown("""
    **Welcome to the Vehicle Analysis Dashboard!**  
    Explore **Sustainability**, **Performance**, **Economy**, **Mileage**, and **Cost** trends through this interactive tool. Key features include:  

    - 📐 **Key Statistics**: Get a comprehensive overview of group performance metrics like highest, lowest, average, and median scores.  
    - 🚀 **Top and Bottom Vehicles**: View the highest and lowest-performing vehicles for each group.  
    - 📊 **Feature Correlation Analysis**: Understand relationships between key variables with heatmaps.  
    - 📈 **Overall Trend Graphs**: Visualize how group scores change over time.  
    - 🔍 **Validation and Feature Trends**: Analyze and validate individual features for inconsistencies, with interactive and detailed visualizations (expandable).  
    """)
    pinata_api_key = "213d8bedb3fdbbee29d9"  # Replace with your Pinata API key
    pinata_secret_api_key = "678bb5c15321ad807c3065ffcad1a72f42cc84a35e352ab39669c2d0f47c02a1"  # Replace with your Pinata secret key

    # Upload to Pinata
    if st.button("Upload to Pinata"):
        try:
            # Check if the keys are valid
            if not pinata_api_key or not pinata_secret_api_key:
                raise ValueError("Pinata API key and Secret key must be provided and non-empty.")

            # File path to upload
            output_pdf = "group_analysis_report.pdf"

            # Upload to Pinata
            pinata_response = upload_to_pinata(output_pdf, pinata_api_key, pinata_secret_api_key)
            if "IpfsHash" in pinata_response:
                st.success("PDF successfully uploaded to Pinata!")
                st.write(f"🔗 [View on IPFS](https://gateway.pinata.cloud/ipfs/{pinata_response['IpfsHash']})")
            else:
                st.error(f"Failed to upload PDF to Pinata: {pinata_response.get('error')}")

        except ValueError as ve:
            st.error(f"Error: {ve}")
        except Exception as e:
            st.error(f"An unexpected error occurred: {str(e)}")

    # Load the dataset from IPFS
    @st.cache_data
    def load_csv_from_ipfs(cid):
        """
        Load a dataset from IPFS using the provided CID.
        """
        url = f"https://gateway.pinata.cloud/ipfs/{cid}"  # Using Pinata's IPFS gateway
        response = requests.get(url)
        if response.status_code == 200:
            csv_data = io.StringIO(response.text)
            return pd.read_csv(csv_data)
        else:
            st.error(f"Failed to fetch data from IPFS. HTTP Status Code: {response.status_code}")
            return None

    # Replace local path with CID
    cid = "Qmaq97iYXo48jgCkHWCfYRWA7L1tfCX2JXvR71y8wnVRAh"
    filtered_file = load_csv_from_ipfs(cid)

    if filtered_file is None:
        st.stop()

    # Encode categorical columns
    def encode_categorical_columns(data, categorical_columns):
        encoder = LabelEncoder()
        for column in categorical_columns:
            if data[column].dtype == 'object':
                data[column] = encoder.fit_transform(data[column].fillna('Unknown'))
        return data

    # Normalize columns
    def normalize_column(column):
        if column.dtype in [np.float64, np.int64]:
            return (column - column.min()) / (column.max() - column.min())
        else:
            return column

    # Compute group scores
    def compute_group_scores(data, groups):
        for group_name, group_info in groups.items():
            columns = group_info["columns"]
            weights = group_info["weights"]

            normalized_data = pd.DataFrame()
            for col in columns:
                if col in data.columns:
                    if group_name == "Sustainability" and col == "co2":
                        normalized_data[col] = 1 - normalize_column(data[col])
                    elif group_name == "Cost" and col in ["fuelCost08", "fuelCostA08"]:
                        normalized_data[col] = 1 - normalize_column(data[col])
                    else:
                        normalized_data[col] = normalize_column(data[col])

            data[f"{group_name} Score"] = sum(
                normalized_data[col] * weights[col] for col in columns if col in normalized_data
            )
        return data

    # Groups and weights definition
    groups = {
        "Sustainability": {
            "columns": ['co2', 'ghgScore', 'fuelType1', 'fuelType2'],
            "weights": {'co2': 0.5, 'ghgScore': 0.4, 'fuelType1': 0.05, 'fuelType2': 0.05}
        },
        "Performance": {
            "columns": ['cylinders', 'displ', 'drive', 'trany'],
            "weights": {'cylinders': 0.4, 'displ': 0.4, 'drive': 0.1, 'trany': 0.1}
        },
        "Economy": {
            "columns": ['comb08', 'barrels08', 'fuelCost08'],
            "weights": {'comb08': 0.5, 'barrels08': 0.3, 'fuelCost08': 0.2}
        },
        "Mileage": {
            "columns": ['comb08', 'range', 'barrels08'],
            "weights": {'comb08': 0.4, 'range': 0.4, 'barrels08': 0.2}
        },
        "Cost": {
            "columns": ['fuelCost08', 'fuelCostA08', 'youSaveSpend'],
            "weights": {'fuelCost08': 0.4, 'fuelCostA08': 0.4, 'youSaveSpend': 0.2}
        }
    }

    # Save group graphs to local directory
    def save_group_graphs(filtered_file, groups, output_dir="group_graphs"):
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        saved_files = []
        for group_name in groups.keys():
            if f"{group_name} Score" in filtered_file.columns:
                group_trend = filtered_file.groupby("year")[f"{group_name} Score"].mean()

                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(group_trend.index, group_trend.values, label=f"{group_name} Score", color="blue", linewidth=2)
                ax.set_title(f"{group_name} Score Trends by Year")
                ax.set_xlabel("Year")
                ax.set_ylabel("Average Score")
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.legend()

                file_path = os.path.join(output_dir, f"{group_name}_score_trend.png")
                fig.savefig(file_path)
                plt.close(fig)
                saved_files.append(file_path)

        return saved_files

    # Create PDF from images
    def create_pdf_from_images(image_files, output_pdf="group_analysis_report.pdf"):
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        for image_file in image_files:
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            title = os.path.basename(image_file).replace("_", " ").replace(".png", "").title()
            pdf.cell(200, 10, txt=title, ln=True, align='C')
            pdf.image(image_file, x=10, y=30, w=190)
        pdf.output(output_pdf)

    # Process data and compute scores
    categorical_columns = ['fuelType1', 'fuelType2', 'drive', 'trany']
    filtered_file = encode_categorical_columns(filtered_file, categorical_columns)
    filtered_file = compute_group_scores(filtered_file, groups)

    # Save graphs and create PDF
    output_dir = "group_graphs"
    image_files = save_group_graphs(filtered_file, groups, output_dir)
    output_pdf = "group_analysis_report.pdf"
    create_pdf_from_images(image_files, output_pdf)
    st.success("Graphs saved locally and PDF created.")
