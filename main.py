import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# Load the dataset
data = pd.read_csv('filtered_file.csv')

# Sidebar for navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Comparison"])

if page == "Home":
    # Home Page
    st.title("Welcome to the Fuel Economy Score App")
    st.write("""
        This app provides insights into fuel economy scores for Toyota and Kia vehicles.
        Use the Comparison page to explore detailed data and visualizations.
    """)


    import streamlit as st
    src="https://us-east-1.quicksight.aws.amazon.com/sn/embed/share/accounts/535002864024/dashboards/ab747687-3a21-46e0-ad9c-e0d2ffc2e7d9?directory_alias=535002864024"
    quicksight_embed_url = "https://example-quicksight-dashboard-url"
    st.components.v1.html(
        f'<iframe src="{src}" width="100%" height="600"></iframe>',
        height=600
    )

    # Add any additional content for the Home page here
    st.write("You can include more information or visuals here for the Home page.")

elif page == "Comparison":
    # Comparison Page
    st.title("Fuel Economy Comparison")
    
    # Filters
    st.write("### Filter Options")
    col1, col2 = st.columns(2)
    with col1:
        make1 = st.selectbox('Select Make 1', data['make'].unique())
        VClass1 = st.selectbox('Select Vehicle Class 1', data['VClass'].unique())
    with col2:
        make2 = st.selectbox('Select Make 2', data['make'].unique())
        VClass2 = st.selectbox('Select Vehicle Class 2', data['VClass'].unique())

    # Filter the data based on selections
    toyota_data = data[data['make'] == make1]
    kia_data = data[data['make'] == make2]

    compact_cars_toyota = toyota_data[toyota_data['VClass'] == VClass1]
    final_table_toyota_compact_cars = compact_cars_toyota.groupby('year').agg({'feScore': 'mean'})

    compact_cars_kia = kia_data[kia_data['VClass'] == VClass2]
    final_table_kia_compact_cars = compact_cars_kia.groupby('year').agg({'feScore': 'mean'})

    avg_fe_score = data[data['VClass'] == 'Compact Cars'].groupby('year').agg({'feScore': 'mean'})

    # Display Data
    st.write("### Data Overview")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{make1} Data**")
        st.write(toyota_data)
    with col2:
        st.write(f"**{make2} Data**")
        st.write(kia_data)

    st.write("### Aggregated Data")
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"**{make1} ({VClass1}) Aggregated by Year**")
        st.write(final_table_toyota_compact_cars)
    with col2:
        st.write(f"**{make2} ({VClass2}) Aggregated by Year**")
        st.write(final_table_kia_compact_cars)

    st.write("### Average Fuel Economy for Compact Cars Across All Makes")
    st.write(avg_fe_score)

    # Plotting
    fig, ax = plt.subplots()
    ax.plot(final_table_kia_compact_cars.index, final_table_kia_compact_cars['feScore'], marker='o', linestyle='-', label=make2)
    ax.plot(final_table_toyota_compact_cars.index, final_table_toyota_compact_cars['feScore'], marker='o', linestyle='-', label=make1)
    ax.plot(avg_fe_score.index, avg_fe_score['feScore'], color='red', linestyle='--', label='Average Fuel Economy Score')
    ax.set_title('Average Fuel Economy Score by Year for Selected Makes and Vehicle Classes')
    ax.set_xlabel('Year')
    ax.set_ylabel('Average Fuel Economy Score')
    ax.set_xticks(range(2021, 2026))
    ax.set_yticks(range(0, 11))
    ax.legend()

    # Display Plot
    st.pyplot(fig)
