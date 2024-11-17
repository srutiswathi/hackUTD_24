import streamlit as st
import pandas as pd
import altair as alt


# Modular functions for HTML and CSS designs
def styled_box_with_chart(title, chart, background_gradient="linear-gradient(135deg, #393939, #1a1a1a)", text_color="white"):
    """
    Generates a styled HTML box with a gradient background and includes a chart.
    Args:
        title (str): The title displayed in the box.
        chart (alt.Chart): The chart to include inside the box.
        background_gradient (str): CSS gradient for the background.
        text_color (str): Color of the text inside the box.
    """
    # Box title
    st.markdown(
        f"""
        <div style="
            background: {background_gradient};
            color: {text_color};
            text-align: center;
            padding: 10px 20px;
            border-radius: 8px 8px 0 0;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
            margin-bottom: -5px;">
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Display the chart
    st.altair_chart(chart, use_container_width=True)


def total_cars():
    # Load data and compute total cars
    data = pd.read_csv('filtered_file.csv')
    toyota_data = data[data['make'] == 'Toyota']
    return len(toyota_data)


def different_models():
    data = pd.read_csv('filtered_file.csv')
    toyota_data = data[data['make'] == 'Toyota']
    return len(toyota_data['model'].unique())


def fe_score_chart():
    # Dropdown to select grouping column
    m1 = st.selectbox('Group by', ['assumed_VClass', 'model'])

    # Load the dataset
    data = pd.read_csv('updated_file.csv')
    toyota_data = data[data['make'] == 'Toyota']

    # Filter data for years 2021 to 2025
    years_of_interest = [2021, 2022, 2023, 2024, 2025]
    fe_score_data = toyota_data[toyota_data['year'].isin(years_of_interest)][[m1, 'year', 'feScore']]

    # Group by selected column and year
    fe_score_table = fe_score_data.groupby([m1, 'year']).mean().reset_index()

    # Create Altair line chart
    line_chart = alt.Chart(fe_score_table).mark_line(point=True).encode(
        x=alt.X('year:O', title='Year', axis=alt.Axis(format='d')),
        y=alt.Y('feScore:Q', title='feScore', scale=alt.Scale(domain=[0, 10])),
        color=alt.Color(f'{m1}:N', legend=alt.Legend(title=m1)),  # Dynamically set color based on m1
        tooltip=[m1, 'year', 'feScore']
    ).properties(
        width=700,
        height=400,
        title=f"Average feScore by {m1.capitalize()} (2021-2025)"
    )

    return line_chart


# Main app functions
def home_page():
    st.title("Toyota Vehicle Dashboard")

    # Layout for styled columns
    col1, col2, col3 = st.columns((1, 1, 2))
    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #393939, #1a1a1a);
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;">
                <h3>Total Cars</h3>
                <p style='font-size: 24px; font-weight: bold;'>{total_cars()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #393939, #1a1a1a);
                color: white;
                text-align: center;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);
                margin-bottom: 20px;">
                <h3>Different Models</h3>
                <p style='font-size: 24px; font-weight: bold;'>{different_models()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
    with col3:
        styled_box_with_chart("Average Fuel Economy Score", fe_score_chart())


# Run the app
if __name__ == "__main__":
    home_page()
