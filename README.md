# La Liga Player Performance Dashboard

## Project Overview

This project is a Streamlit web application designed to visualize and analyze player performance statistics from the 2022-2023 La Liga season. It assists football scouts, analysts, and coaches in making data-driven decisions by allowing them to:

1.  **Identify Top Performers:** Find standout players based on selected per-90-minute metrics using scatter plots and ranked bar charts.
2.  **Compare Players:** Directly compare the detailed statistical profiles of two selected players side-by-side.
3.  **Analyze Opponents:** Review the key statistics for an entire opponent's squad, highlighting potential threats based on chosen metrics.

The dashboard design emphasizes clarity, efficiency, and cognitive ergonomics, applying principles of data visualization and cognitive science.

## Files Included

*   `dashboard.py`: The main Streamlit application script.
*   `data_preparation.py`: (Optional inclusion) The script used to process the raw data from FBref into the final dataset.
*   `laliga_player_stats_processed.csv`: The final, processed dataset used by the dashboard application.
*   `requirements.txt`: Lists the required Python packages and their versions.
*   `README.md`: This file.
*   `Rationale_Gael_Mensa.pdf`: The separate document explaining the design rationale.
*   *(Optional)* Raw FBref CSV files (`standard_stats.csv`, `shooting_stats.csv`, etc.)

## Data Source

Player statistics for the 2022-2023 La Liga season were sourced from [FBref.com](https://fbref.com/en/comps/12/2022-2023/stats/2022-2023-La-Liga-Stats).

## Setup Instructions

1.  **Clone or Download:** Get the project files onto your local machine.
2.  **Navigate to Directory:** Open your terminal or command prompt and change directory into the project folder (e.g., `cd path/to/Activity3_Data_Visualization`).
3.  **(Recommended) Create a Virtual Environment:**
    *   `python -m venv venv`
    *   Activate it:
        *   macOS/Linux: `source venv/bin/activate`
        *   Windows: `venv\Scripts\activate`
4.  **Install Requirements:** Install the necessary Python packages using pip:
    *   `pip install -r requirements.txt`

## How to Run the Dashboard

1.  Ensure you are in the project directory in your terminal and your virtual environment (if used) is activated.
2.  Run the Streamlit application using the command:
    *   `streamlit run dashboard.py`
3.  The dashboard should automatically open in your default web browser. Use the sidebar filters and mode selector to explore the data.