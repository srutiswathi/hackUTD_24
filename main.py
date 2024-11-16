import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Simulate some data
data = pd.DataFrame({
    "Company": ["Toyota", "Honda", "Ford", "Chevrolet", "Tesla"],
    "Car Type": ["Sedan", "SUV", "Truck", "Coupe", "Electric"],
    "FE Score": [85, 90, 75, 80, 95],
    "Time": ["2023 Q1", "2023 Q2", "2023 Q3", "2023 Q4", "2024 Q1"]
})

# App title
st.markdown(
    "<h1 style='text-align: left; color: black; background-color: #d3d3d3;'>Toyota</h1>",
    unsafe_allow_html=True,
)

# Layout: Filters and Graph side by side
col1, col2 = st.columns([1, 3])

# Filters in the first column
with col1:
    st.markdown("### Filters")

    # Company filter
    selected_company = st.selectbox("Company", options=data["Company"].unique())

    # Car Type filter
    selected_car_type = st.selectbox("Car Type", options=data["Car Type"].unique())

    # Apply button
    if st.button("Apply"):
        st.success("Filters applied!")

# Graph in the second column
with col2:
    st.markdown("### FE Score Over Time")

    # Filter the data based on user input
    filtered_data = data[
        (data["Company"] == selected_company) & (data["Car Type"] == selected_car_type)
    ]

    # Create the graph
    if not filtered_data.empty:
        fig, ax = plt.subplots()
        ax.plot(filtered_data["Time"], filtered_data["FE Score"], marker="o", color="red")
        ax.set_xlabel("Time")
        ax.set_ylabel("FE Score")
        ax.set_title(f"FE Score Trend for {selected_company} ({selected_car_type})")
        st.pyplot(fig)
    else:
        st.warning("No data available for the selected filters.")
