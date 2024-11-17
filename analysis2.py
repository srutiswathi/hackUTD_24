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
    remaining()
        
def remaining():
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

    def save_plots_to_pdf(pdf_path, filtered_file, groups):
        """
        Save generated plots to a PDF file, one plot for each group.
        """
        pdf = FPDF()
        pdf.set_auto_page_break(auto=True, margin=15)

        for group_name in groups.keys():
            if f"{group_name} Score" in filtered_file.columns:
                # Calculate the trend for the current group
                group_trend = filtered_file.groupby("year")[f"{group_name} Score"].mean()

                # Create a plot for this group
                fig, ax = plt.subplots(figsize=(10, 6))
                ax.plot(group_trend.index, group_trend.values, label=f"{group_name} Score", color="blue", linewidth=2)
                ax.set_title(f"{group_name} Score Trends by Year")
                ax.set_xlabel("Year")
                ax.set_ylabel("Average Score")
                ax.grid(True, linestyle="--", alpha=0.6)
                ax.legend()

                # Save the plot as a temporary image
                temp_plot_path = "temp_plot.png"
                fig.savefig(temp_plot_path)
                plt.close(fig)

                # Add the plot to the PDF
                pdf.add_page()
                pdf.set_font("Arial", size=12)
                pdf.cell(200, 10, txt=f"{group_name} Score Trends by Year", ln=True, align='C')
                pdf.image(temp_plot_path, x=10, y=30, w=190)

                # Remove the temporary plot file
                os.remove(temp_plot_path)

        # Output the final PDF
        pdf.output(pdf_path)


    # Example of how to save the plots to PDF and upload to Pinata
    pdf_path = "vehicle_analysis_report.pdf"
    save_plots_to_pdf(pdf_path, filtered_file, groups)


    # Upload the PDF to Pinata without using 'file_name' argument
    #pinata_response = upload_to_pinata(pdf_path)

    # Check if the upload was successful and display the IPFS URL
    # if pinata_response:
    #     st.write(f"File uploaded successfully! View it on IPFS: https://gateway.pinata.cloud/ipfs/{pinata_response['IpfsHash']}")
    # else:
    #     st.error("Failed to upload the file to Pinata.")

    # Now use this in the main analysis code
    # pdf_path = "vehicle_analysis_plots.pdf"
    # save_plots_to_pdf(pdf_path, filtered_file, groups)


    # Pinata API credentials
    PINATA_API_KEY = "213d8bedb3fdbbee29d9"  # Replace with your API key
    PINATA_SECRET_API_KEY = "678bb5c15321ad807c3065ffcad1a72f42cc84a35e352ab39669c2d0f47c02a1"  # Replace with your secret key

    # Save and upload PDF
    # if st.button("Save and Pin PDF"):
    #     pdf_path = "vehicle_analysis_report.pdf"
        
    #     # Generate and save the plots into a PDF
    #     save_plots_to_pdf(pdf_path, filtered_file, groups)  # Ensure this function exists and works correctly

    #     # Initialize pinata_response to None
    #     pinata_response = None
        
    #     # Upload the PDF to Pinata
    #     try:
    #         pinata_response = upload_to_pinata(
    #             file_path=pdf_path,
    #             pinata_api_key=PINATA_API_KEY,
    #             pinata_secret_api_key=PINATA_SECRET_API_KEY
    #         )
    #     except Exception as e:
    #         st.error(f"An error occurred during upload: {str(e)}")

    #     # Handle the response
    #     if pinata_response:
    #         st.success("PDF report saved and pinned to Pinata!")
    #         st.write(f"🔗 [View Report on IPFS](https://gateway.pinata.cloud/ipfs/{pinata_response['IpfsHash']})")
    #     else:
    #         st.error("Failed to upload PDF to Pinata. Please check your API keys and network connection.")


    # Validate and plot columns
    def validate_and_plot_columns(data, group_name, group_info):
        inconsistent_features = []

        with st.expander(f"🔍 Validation and Feature Trends for {group_name}", expanded=False):
            for feature in group_info["columns"]:
                if feature in data.columns:
                    # Calculate yearly trend
                    trend = data.groupby("year")[feature].mean()

                    # Check for monotonicity
                    if not np.all(np.diff(trend.values) >= 0) and not np.all(np.diff(trend.values) <= 0):
                        inconsistent_features.append(feature)
                        st.warning(f"🚨 Feature **{feature}** trend is not monotonic. Please review the data.")
                    else:
                        st.success(f"✅ Feature **{feature}** shows a consistent trend over the years.")

                    # Smoothing the trend for visualization
                    smoothed_trend = trend.rolling(window=2).mean()
                    
                    # Plot original and smoothed trend as a line graph
                    fig, ax = plt.subplots(figsize=(10, 6))
                    ax.plot(trend.index, trend.values, marker='o', label="Original Trend", color="blue", linewidth=2)
                    ax.plot(trend.index, smoothed_trend, linestyle="--", marker='o', label="Smoothed Trend", color="orange", linewidth=2)
                    ax.set_title(f"{feature} Trend: Original vs. Smoothed", fontsize=14)
                    ax.set_xlabel("Year", fontsize=12)
                    ax.set_ylabel(feature, fontsize=12)
                    ax.legend()
                    ax.grid(True, linestyle="--", alpha=0.6)
                    st.pyplot(fig)

            # Display overall feedback based on validation
            if inconsistent_features:
                st.warning(f"🚨 Inconsistent trends found for: {', '.join(inconsistent_features)}.")
            else:
                st.success("✅ All features show consistent trends.")

    # Apply encoding and calculate scores
    categorical_columns = ['fuelType1', 'fuelType2', 'drive', 'trany']
    filtered_file = encode_categorical_columns(filtered_file, categorical_columns)
    filtered_file = compute_group_scores(filtered_file, groups)

    # Create columns for the dropdown and the statistics
    col= st.columns([10, 3])

    # Add the dropdown next to the Key Statistics

    with col[-1]:
        group_name = st.selectbox("Select Group", ["Sustainability", "Performance", "Economy", "Mileage", "Cost"])
    with col[0]:
        st.subheader(f"🔑 Key Statistics for {group_name}")

    # Display Key Metrics in Styled Boxes with Explanations


    # Compute metrics
    highest_score = filtered_file[f"{group_name} Score"].max()
    lowest_score = filtered_file[f"{group_name} Score"].min()
    average_score = filtered_file[f"{group_name} Score"].mean()
    median_score = filtered_file[f"{group_name} Score"].median()
    total_vehicles = len(filtered_file)
    above_avg_vehicles = len(filtered_file[filtered_file[f"{group_name} Score"] > average_score])

    # Define box style
    box_style = """
        <div style="
            background-color: #1e1e1e; 
            padding: 20px; 
            margin: 10px; 
            border-radius: 8px; 
            box-shadow: 2px 2px 6px rgba(0,0,0,0.1); 
            text-align: center;">
            <h2 style="color: #fff; margin: 0;">{value}</h2>
            <p style="color: #a1a1a1; margin: 5px 0 0;">{label}</p>
            <p style="font-size: 10px; color: gray;">{description}</p>
        </div>
    """

    # Use columns for layout
    col3, col4, col5 = st.columns(3)

    with col3:
        st.markdown(box_style.format(
            value=f"{highest_score:.2f}",  # Max score achieved
            label="📈 Max Score Achieved", 
            description="The highest score achieved by any vehicle in this category."
        ), unsafe_allow_html=True)

    with col4:
        st.markdown(box_style.format(
            value=f"{average_score:.2f}",  # Overall average score
            label="📊 Average Score", 
            description="The overall average score across all vehicles in this category."
        ), unsafe_allow_html=True)

    with col5:
        st.markdown(box_style.format(
            value=f"{lowest_score:.2f}",  # Minimum score
            label="❌ Min Score", 
            description="The lowest score achieved by any vehicle in this category."
        ), unsafe_allow_html=True)

    # Add the remaining metrics
    col6, col7, col8 = st.columns(3)

    with col6:
        st.markdown(box_style.format(
            value=f"{median_score:.2f}", 
            label="📈 Median Score", 
            description="The middle value of scores for vehicles in this category."
        ), unsafe_allow_html=True)

    with col7:
        st.markdown(box_style.format(
            value=f"{total_vehicles}", 
            label="🚗 Total Vehicles", 
            description="The total number of vehicles analyzed in this category."
        ), unsafe_allow_html=True)

    with col8:
        st.markdown(box_style.format(
            value=f"{above_avg_vehicles}", 
            label="🏆 Above Avg Vehicles", 
            description="The number of vehicles scoring above the average score."
        ), unsafe_allow_html=True)

    # Group-Specific Trend Plot
    st.subheader(f"📈 {group_name} Score Trends by Year")
    group_trend = filtered_file.groupby("year")[f"{group_name} Score"].mean()
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(group_trend.index, group_trend.values, label=f"{group_name} Score", color="blue", linewidth=2)
    ax.set_title(f"{group_name} Score Trends by Year")
    ax.set_xlabel("Year")
    ax.set_ylabel("Average Score")
    ax.grid(True, linestyle="--", alpha=0.6)
    ax.legend()
    st.pyplot(fig)

    # Always-visible insights
    st.subheader(f"🚀 Top 5 Vehicles by {group_name} Score")
    top_5 = filtered_file.nlargest(5, f"{group_name} Score")
    st.dataframe(top_5[["make", "model", f"{group_name} Score"]])

    st.subheader(f"⚠️ Bottom 5 Vehicles by {group_name} Score")
    bottom_5 = filtered_file.nsmallest(5, f"{group_name} Score")
    st.dataframe(bottom_5[["make", "model", f"{group_name} Score"]])

    st.subheader(f"📊 Correlation Heatmap for {group_name}")
    group_columns = groups[group_name]["columns"]
    correlation_data = filtered_file[group_columns]
    correlation_matrix = correlation_data.corr()

    # Plot heatmap
    fig, ax = plt.subplots(figsize=(10, 6))
    sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", ax=ax)
    ax.set_title(f"{group_name} Feature Correlations", fontsize=16)
    st.pyplot(fig)

    # Group-specific trends and validation
    validate_and_plot_columns(filtered_file, group_name, groups[group_name])

    # # Save the processed file for further use
    # local_file_path = "/Users/srutikarthikeyan/Desktop/hackUTD/hackUTD_24/processed_file_analysis.csv"  # Define local file path
    # filtered_file.to_csv(local_file_path, index=False)  # Save the processed file

    # # Save the generated plots to a PDF
    # pdf_path = "vehicle_analysis_plots.pdf"
    # save_plots_to_pdf(pdf_path)

    # # Upload the PDF file to Pinata
    # pinata_response = upload_to_pinata(pdf_path)

    # # Check if the upload was successful and display the IPFS URL
    # if pinata_response:
    #     st.write(f"File uploaded successfully! View it on IPFS: https://gateway.pinata.cloud/ipfs/{pinata_response['IpfsHash']}")
    # else:
    #     st.error("Failed to upload the file to Pinata.")