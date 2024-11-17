import streamlit as st
import pandas as pd
import altair as alt



# Modular functions for HTML and CSS designs
def styled_box_with_chart(title, chart, background_gradient="linear-gradient(135deg, #7a0000, #280000)", text_color="white"):
    """
    Generates a styled HTML box with a gradient background and includes a chart.
    Args:
        title (str): The title displayed in the box.
        chart (alt.Chart): The chart to include inside the box.
        background_gradient (str): CSS gradient for the background.
        text_color (str): Color of the text inside the box.
    """
    # Box with border, rounded corners, and padding
    st.markdown(
        f"""
        <div style="
            background: {background_gradient};
            color: {text_color};
            text-align: center;
            padding: 10px;
            border: 3px solid #0d1b2a;  /* Navy blue border */
            border-radius: 27px;       /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
            margin-bottom: 10px;">
            <h3>{title}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    # Display the chart
    st.altair_chart(chart, use_container_width=True)


def total_cars():
    data = pd.read_csv('./filtered_file.csv')
    toyota_data = data[data['make'] == 'Toyota']
    return len(toyota_data)


def different_models(m1, data):
    toyota_data = data[data['make'] == 'Toyota']
    return len(toyota_data[m1].unique())


def model_or_class(m1):
    return str(m1)


def fe_score_chart(m1, data):
    # Load the dataset
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
        color=alt.Color(f'{m1}:N', legend=None),  # Removed the legend
        tooltip=[m1, 'year', 'feScore']
    ).properties(
        width=700,
        height=400,
    )

    return line_chart



def pie_chart(m1, data):
    toyota_data = data[data['make'] == 'Toyota']
    pie_data = toyota_data[m1].value_counts().reset_index()
    pie_data.columns = [m1, 'count']

    pie_chart = alt.Chart(pie_data).mark_arc(innerRadius=50).encode(
        theta=alt.Theta('count:Q', title="Count"),
        color=alt.Color(f'{m1}:N', legend=None),  # Removed the legend
        tooltip=[f'{m1}:N', 'count:Q']
    ).properties(
        width=200,  # Reduced width
        height=200,  # Reduced height
    )


    return pie_chart




def percentage_bar_chart(m1, data):
    # Filter for Toyota vehicles
    toyota_data = data[data['make'] == 'Toyota']

    # Group data by the selected column (m1) and calculate mean values
    grouped_data = toyota_data.groupby(m1)[['city08U', 'highway08U', 'comb08U']].mean().reset_index()

    # Melt the data to have a long format suitable for Altair
    melted_data = grouped_data.melt(id_vars=m1, var_name='Metric', value_name='Value')

    # Create a bar chart
    bar_chart = alt.Chart(melted_data).mark_bar().encode(
        x=alt.X('Value:Q', title='Average Value'),
        y=alt.Y(f'{m1}:N', title=m1.capitalize(), sort='-x'),
        color=alt.Color('Metric:N', legend=alt.Legend(title="Fuel Efficiency Metric")),
        tooltip=[f'{m1}:N', 'Metric:N', 'Value:Q']
    ).properties(
        width=700,
        height=400,
    )

    return bar_chart


def co2_bar_chart(m1, data):
    """
    Creates a bar chart with 'comb08U', 'city08U', 'highway08U' on the x-axis 
    and average CO2 values on the y-axis based on the selected m1.
    """
    # Filter for Toyota vehicles
    toyota_data = data[data['make'] == 'Toyota']

    # Group by the selected column (m1) and calculate the mean CO2 for each metric
    grouped_data = toyota_data.groupby(m1)[['comb08U', 'city08U', 'highway08U', 'co2']].mean().reset_index()

    # Melt the data to have a long format suitable for Altair
    melted_data = grouped_data.melt(
        id_vars=m1, 
        value_vars=['comb08U', 'city08U', 'highway08U'], 
        var_name='Metric', 
        value_name='Average_CO2'
    )

    # Create the bar chart
    bar_chart = alt.Chart(melted_data).mark_bar().encode(
        x=alt.X('Metric:N', title="Metric"),
        y=alt.Y('Average_CO2:Q', title="Average CO2 Value"),
        color=alt.Color('Metric:N', legend=None),
        tooltip=[f'{m1}:N', 'Metric:N', 'Average_CO2:Q']
    ).properties(
        width=700,
        height=400,
    )

    return bar_chart


def home_page():
    st.markdown(
        """
        <style>
        body {
            background: linear-gradient(195deg, #000000, #f32929); /* Gradient background */
            color: white;
        }
        .stApp {
            background: linear-gradient(185deg, #000000, #f32929); /* Gradient for the app background */
        }
        </style>
        """,
        unsafe_allow_html=True
)


    st.title("Toyota Vehicle Dashboard")
    m1 = st.selectbox('Group by', ['assumed_VClass', 'baseModel'])
    data = pd.read_csv('./updated_file.csv')
    st.write(data.head())

    # Layout for styled columns
    col1, col2, col3 = st.columns((1, 1, 2))
    with col1:
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #2b2d42, #3a3a3a);
                color: white;
                text-align: center;
                padding: 20px;
                border: 2px solid #0d1b2a;  /* Navy blue border */
                border-radius: 32px;       /* Rounded corners */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
                margin-bottom: 15px;">
                <h3>Total Cars</h3>
                <p style='font-size: 24px; font-weight: bold;'>{total_cars()}</p>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #2b2d42, #3a3a3a);
                color: white;
                text-align: center;
                padding: 20px;
                border: 2px solid #0d1b2a;  /* Navy blue border */
                border-radius: 32px;       /* Rounded corners */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
                margin-bottom: 15px;">
                <h3>Different {model_or_class(m1)}</h3>
                <p style='font-size: 24px; font-weight: bold;'>{different_models(m1, data)}</p>
            </div>
            """,
            unsafe_allow_html=True
        )


    with col2:
        # Styling for pie chart
        st.markdown(
            f"""
            <div style="
                background: linear-gradient(135deg, #2b2d42, #3a3a3a);
                color: white;
                text-align: center;
                padding: 10px;
                border: 2px solid #0d1b2a;  /* Reduced border width */
                border-radius: 32px;       /* Rounded corners */
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
                width:100px; /* Adjusted box width */
                max-width: 200px;          /* Maximum width of the container */
                margin-bottom: 10px;">
                <h3>Distribution of {model_or_class(m1)}</h3>
            </div>
            """,
            unsafe_allow_html=True
        )
        st.altair_chart(pie_chart(m1, data), use_container_width=True)

    with col3:
    # Add space for alignment
        st.write(" ")  # Spacer
        st.markdown("<div style='margin-left: 20px;'>", unsafe_allow_html=True)  # Add left margin
        st.image(
            "./Toyota Supra.png",
            caption="Toyota",
            width=450  # Adjust width as needed
        )
        st.markdown("</div>", unsafe_allow_html=True)  # Close the div




    
    # Add spacing before line chart
    st.markdown(
        """
        <div style="height: 50px;"></div>
        """,
        unsafe_allow_html=True
    )
    
    # Styling for line chart
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #2b2d42, #3a3a3a);
            color: white;
            text-align: center;
            padding: 20px;
            border: 3px solid #0d1b2a;  /* Navy blue border */
            border-radius: 32px;       /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
            margin-bottom: 15px;">
            <h3>Average feScore by {model_or_class(m1)}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.altair_chart(fe_score_chart(m1, data), use_container_width=True)


    # Styling for percentage bar chart
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg,#2b2d42, #3a3a3a);
            color: white;
            text-align: center;
            padding: 20px;
            border: 3px solid #0d1b2a;  /* Navy blue border */
            border-radius: 32px;       /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
            margin-bottom: 15px;">
            <h3>Fuel Efficiency Metrics by {model_or_class(m1)}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.altair_chart(percentage_bar_chart(m1, data), use_container_width=True)

    # Styling for CO2 bar chart
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #2b2d42, #3a3a3a);
            color: white;
            text-align: center;
            padding: 20px;
            border: 3px solid #0d1b2a;  /* Navy blue border */
            border-radius: 32px;       /* Rounded corners */
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.5);  /* Subtle shadow */
            margin-bottom: 15px;">
            <h3>CO2 Emissions by Metric and {model_or_class(m1)}</h3>
        </div>
        """,
        unsafe_allow_html=True
    )
    st.altair_chart(co2_bar_chart(m1, data), use_container_width=True)


if __name__ == "__main__":
    home_page()


