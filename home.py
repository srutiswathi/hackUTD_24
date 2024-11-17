import streamlit as st
import pandas as pd


# Modular functions for HTML and CSS designs
def styled_box(title, content, background_gradient="linear-gradient(135deg, #393939, #1a1a1a)", text_color="white"):
    """
    Generates a styled HTML box with a gradient background.
    Args:
        title (str): The title displayed in the box.
        content (str): The main content displayed in the box.
        background_gradient (str): CSS gradient for the background.
        text_color (str): Color of the text inside the box.
    Returns:
        str: HTML content for the styled box.
    """
    return f"""
    <div style="
        background: {background_gradient};
        color: {text_color};
        text-align: center;
        padding: 20px;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.2);">
        <h3>{title}</h3>
        <p style="font-size: 24px; font-weight: bold;">{content}</p>
    </div>
    """


# Main app functions
def home_page():
    st.title("Welcome to the Fuel Economy Score App")
    st.write("""
        This app provides insights into fuel economy scores for Toyota and Kia vehicles.
        Use the Comparison page to explore detailed data and visualizations.
    """)
    st.write("Additional information or visuals can be added here.")
    st.markdown(
        """
        <div style='background-color: #f0f0f0; width: 100%;'>
            <p style='text-align: center;'>This is a full-width horizontal div with a slight gray color.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Layout for styled columns
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(
            styled_box("Total Cars", total_cars()),
            unsafe_allow_html=True
        )
    with col2:
        st.write("Additional content can be added here.")


def total_cars():
    # Load data and compute total cars
    data = pd.read_csv('filtered_file.csv')
    toyota_data = data[data['make'] == 'Toyota']
    return len(toyota_data)


# Run the app
if __name__ == "__main__":
    home_page()
