# Import necessary libraries
import streamlit as st              # For creating the web app interface
import pandas as pd                 # For data manipulation and analysis
import plotly.express as px         # For creating interactive plots easily
import plotly.graph_objects as go   # For more control over plots (used for table styling here)
import numpy as np                  # For numerical operations (used for handling potential NaNs)

# --- Page Configuration ---
# Set Streamlit page configuration for title, layout, and initial sidebar state
st.set_page_config(
    page_title="La Liga Player Performance Dashboard",
    layout="wide",                  # Use the full page width
    initial_sidebar_state="expanded" # Keep the sidebar open by default
)

# --- Data Loading Function ---
# Cache the data loading function to avoid reloading data on every interaction
@st.cache_data
def load_data(filepath):
    """
    Loads player statistics data from a CSV file, performs basic cleaning,
    and ensures correct data types.

    Args:
        filepath (str): The path to the CSV file.

    Returns:
        pandas.DataFrame or None: The loaded and cleaned DataFrame, or None if loading fails.
    """
    try:
        # Read the CSV file into a pandas DataFrame
        df = pd.read_csv(filepath)

        # Identify potential numeric columns (per 90 stats, age, minutes, percentages)
        numeric_cols = [col for col in df.columns if '_per90' in col or col in ['Age', 'Min', '90s', 'SoT%', 'Cmp%']]
        # Ensure key identifier/categorical columns are not accidentally included
        numeric_cols = [col for col in numeric_cols if col not in ['Player', 'Squad', 'Pos']]

        # Convert identified columns to numeric, setting errors='coerce' turns invalid parsing into NaN
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce')

        # Fill any resulting NaN values in numeric columns with 0
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # Ensure Player column is string type for consistent use in selectors
        df['Player'] = df['Player'].astype(str)

        # Create a 'Pos_Primary' column by taking the first position listed (handles cases like "FW,MF")
        df['Pos_Primary'] = df['Pos'].apply(lambda x: x.split(',')[0].strip() if pd.notna(x) else 'Unknown')

        # Ensure 'Squad' is string type and handle potential 'nan' strings from data source/prep
        df['Squad'] = df['Squad'].astype(str).replace('nan', 'Unknown')

        # Sort the DataFrame by player name alphabetically for consistent dropdown lists
        return df.sort_values(by="Player")

    except FileNotFoundError:
        # Display an error message in the app if the file isn't found
        st.error(f"Error: The file {filepath} was not found. Make sure it's in the correct directory.")
        return None
    except Exception as e:
        # Display a generic error message for other loading issues
        st.error(f"An error occurred loading the data: {e}")
        return None

# --- Load the Processed Data ---
# Call the load_data function to get the main DataFrame for the app
df = load_data('laliga_player_stats_processed.csv')

# Stop the app execution if data loading failed
if df is None:
    st.stop()

# --- Define Metric Choices & Column Sets ---
# Dictionary mapping user-friendly metric names (for UI) to actual DataFrame column names
metric_options_dict = {
    'Goals per 90': 'Gls_per90', 'Assists per 90': 'Ast_per90',
    'xG per 90': 'xG_per90', 'xA per 90': 'xAG_per90',
    'Key Passes per 90': 'KP_per90', 'Prog Passes per 90': 'PrgP_per90',
    'Success Dribbles per 90': 'Succ_per90', 'Prog Carries per 90': 'PrgC_per90',
    'Tackles Won per 90': 'TklW_per90', 'Interceptions per 90': 'Int_per90',
    'SCA per 90': 'SCA_per90', 'GCA per 90': 'GCA_per90',
    'Pass Comp %': 'Cmp%', 'Shot Target %': 'SoT%'
}
# Add Shots per 90 to the dictionary if the column exists in the loaded data
if 'Shots_per90' in df.columns:
     metric_options_dict['Shots per 90'] = 'Shots_per90'
# Create a list of the user-friendly names for dropdown selectors
metric_display_names = list(metric_options_dict.keys())

# Dictionary mapping display names to actual columns needed for the Player Comparison table
comparison_cols_info = {
    'Player': 'Player', 'Squad': 'Squad', 'Pos': 'Pos', 'Age': 'Age', 'Min': 'Min',
    'Goals per 90': 'Gls_per90', 'Assists per 90': 'Ast_per90',
    'xG per 90': 'xG_per90', 'xA per 90': 'xAG_per90',
    # Conditionally add Shots per 90 using dictionary unpacking
    **({'Shots per 90': 'Shots_per90'} if 'Shots_per90' in df.columns else {}),
    'Key Passes per 90': 'KP_per90', 'Prog Passes per 90': 'PrgP_per90',
    'Success Dribbles per 90': 'Succ_per90', 'Prog Carries per 90': 'PrgC_per90',
    'Tackles Won per 90': 'TklW_per90', 'Interceptions per 90': 'Int_per90',
    'SCA per 90': 'SCA_per90', 'GCA per 90': 'GCA_per90',
    'Pass Comp %': 'Cmp%', 'Shot Target %': 'SoT%'
}
# Get the list of actual column names needed for the comparison table
comparison_actual_cols = list(comparison_cols_info.values())

# Define the specific columns to display in the Opponent Analysis table
opponent_analysis_cols = [
    'Player', 'Pos', 'Age', 'Min',
    'Gls_per90', 'Ast_per90', 'xG_per90', 'xAG_per90',
    # Conditionally add Shots_per90 using list unpacking
    *(['Shots_per90'] if 'Shots_per90' in df.columns else []),
    'KP_per90', 'PrgP_per90', 'Succ_per90', 'TklW_per90'
]

# --- Sidebar Filters ---
# Add a header for the filters section in the sidebar
st.sidebar.header("Filters")

# Season selector (currently static, can be expanded)
seasons = ["2022-2023"]
selected_season = st.sidebar.selectbox("Select Season", seasons)

# Get unique team names from the *original* DataFrame for opponent selection
# Exclude 'TOT' (transfer total row) and 'Unknown' squads if they exist
all_teams = sorted([team for team in df['Squad'].unique() if team != 'TOT' and team != 'Unknown'])

# Get unique primary positions for the Position filter
all_positions = df['Pos_Primary'].unique()
# Define a preferred order for positions in the multiselect widget
position_order = ['GK', 'DF', 'MF', 'FW', 'Unknown']
# Sort the positions based on the defined order, placing others at the end
sorted_positions = sorted(all_positions, key=lambda x: position_order.index(x) if x in position_order else len(position_order))
# Create the multiselect widget for positions, defaulting to outfield players
selected_positions = st.sidebar.multiselect("Filter by Position(s)", sorted_positions, default=['FW', 'MF', 'DF'])

# Create a slider to filter players by minimum minutes played
min_minutes_threshold = st.sidebar.slider(
    "Filter by Minimum Minutes Played",
    min_value=0,
    max_value=int(df['Min'].max()),  # Set max value based on data
    value=500,                      # Default minimum minutes
    step=50                         # Increment step for the slider
)

# Create radio buttons to select the dashboard's analysis mode
analysis_mode = st.sidebar.radio(
    "Select Analysis Mode",
    ("Identify Top Performers", "Compare Players", "Analyze Opponent"),
    key='analysis_mode' # Assign a key to help maintain widget state
)

# --- Filtering Data Based on Sidebar Selections ---
# Apply the minimum minutes filter to the main DataFrame
df_filtered = df[df['Min'] >= min_minutes_threshold].copy()
# Apply the position filter if any positions are selected
if selected_positions:
    df_filtered = df_filtered[df_filtered['Pos_Primary'].isin(selected_positions)]

# Generate the list of players available *after* filtering (for player comparison selectors)
player_list = df_filtered['Player'].unique().tolist() # Already sorted due to initial sort

# --- Main Panel Display ---
# Set the main title of the dashboard
st.title("La Liga Player Performance Dashboard")
# Display the selected season and analysis mode
st.write(f"Season: {selected_season} | Mode: {analysis_mode}")
# Display the currently active filters
position_text = ', '.join(selected_positions) if selected_positions else 'None'
st.write(f"Displaying data for players in positions: **{position_text}** with at least **{min_minutes_threshold}** minutes played.")
# Add a visual separator
st.divider()

# --- Display Content Based on Selected Mode ---

# Logic for "Identify Top Performers" mode
if analysis_mode == "Identify Top Performers":
    st.header("Identify Top Performers")

    # Display metric selectors in the sidebar only for this mode
    st.sidebar.subheader("Chart Metrics")
    # Set default indices for selectors, checking if defaults exist
    x_default_idx = metric_display_names.index('xG per 90') if 'xG per 90' in metric_display_names else 0
    y_default_idx = metric_display_names.index('xA per 90') if 'xA per 90' in metric_display_names else 1
    bar_default_idx = metric_display_names.index('Goals per 90') if 'Goals per 90' in metric_display_names else 0

    # Create select boxes for choosing chart metrics
    x_axis_metric_display = st.sidebar.selectbox("Select X-axis Metric", metric_display_names, index=x_default_idx)
    y_axis_metric_display = st.sidebar.selectbox("Select Y-axis Metric", metric_display_names, index=y_default_idx)
    bar_chart_metric_display = st.sidebar.selectbox("Select Bar Chart Metric", metric_display_names, index=bar_default_idx)

    # Get the actual DataFrame column names corresponding to the selected display names
    x_axis_metric = metric_options_dict[x_axis_metric_display]
    y_axis_metric = metric_options_dict[y_axis_metric_display]
    bar_chart_metric = metric_options_dict[bar_chart_metric_display]

    # Check if the selected metric columns actually exist in the filtered DataFrame
    plot_cols_exist = all(col in df_filtered.columns for col in [x_axis_metric, y_axis_metric, bar_chart_metric])

    if not plot_cols_exist:
         # Show warning if a selected metric column is missing
         st.warning(f"One or more selected metric columns not found in the data for plotting.")
    elif df_filtered.empty:
         # Show warning if no players match the current filters
         st.warning("No players match the current filter criteria.")
    else:
        # --- Scatter Plot ---
        st.subheader(f"{y_axis_metric_display} vs. {x_axis_metric_display}")
        # Define data to show on hover
        hover_data_scatter = ["Squad", "Age", "Min", x_axis_metric, y_axis_metric]
        if 'Shots_per90' in df_filtered.columns: hover_data_scatter.append('Shots_per90') # Add conditionally

        # Create the scatter plot using Plotly Express
        fig_scatter = px.scatter(
            df_filtered,                            # Data source
            x=x_axis_metric,                        # X-axis metric column
            y=y_axis_metric,                        # Y-axis metric column
            color="Pos_Primary",                    # Color points by primary position
            hover_name="Player",                    # Show player name on hover
            hover_data=hover_data_scatter,          # Additional data on hover
            title=f"Player Performance: {y_axis_metric_display} vs. {x_axis_metric_display}",
            labels={                                # Map column names to readable labels
                x_axis_metric: x_axis_metric_display,
                y_axis_metric: y_axis_metric_display,
                "Pos_Primary": "Position"
            },
            template="plotly_white"                 # Use a clean plot theme
        )
        # Update layout properties (axis titles, legend, height)
        fig_scatter.update_layout(
             xaxis_title=x_axis_metric_display,
             yaxis_title=y_axis_metric_display,
             legend_title_text='Position',
             height=500
        )
        # Update marker appearance (size, opacity)
        fig_scatter.update_traces(marker=dict(size=8, opacity=0.7))
        # Display the plot in Streamlit
        st.plotly_chart(fig_scatter, use_container_width=True)
        # Add explanatory text for the chart
        st.markdown("""
        **How to Read:** This chart plots players based on two selected performance metrics (per 90 minutes).
        Players further to the **top-right** generally excel in both selected metrics. Color indicates primary position.
        Hover over points for player details. Helps identify players with specific statistical profiles (e.g., high xG and high xA).
        """)
        st.divider()

        # --- Bar Chart ---
        st.subheader(f"Top 15 Players by {bar_chart_metric_display}")
        # Get the top 15 players based on the selected bar chart metric, then sort ascending for plotting correctly
        df_top15 = df_filtered.nlargest(15, bar_chart_metric).sort_values(by=bar_chart_metric, ascending=True)
        # Define data to show on hover
        hover_data_bar = ["Squad", "Age", "Min", bar_chart_metric]
        if 'Shots_per90' in df_filtered.columns: hover_data_bar.append('Shots_per90') # Add conditionally

        # Create the horizontal bar chart using Plotly Express
        fig_bar = px.bar(
            df_top15,                               # Data source (top 15 players)
            x=bar_chart_metric,                     # Metric values on X-axis
            y="Player",                             # Player names on Y-axis
            orientation='h',                        # Make it a horizontal chart
            color="Pos_Primary",                    # Color bars by primary position
            hover_name="Player",                    # Show player name on hover
            hover_data=hover_data_bar,              # Additional data on hover
            title=f"Top 15 Players by {bar_chart_metric_display}",
            labels={                                # Map column names to readable labels
                bar_chart_metric: bar_chart_metric_display,
                "Player": "Player",
                "Pos_Primary": "Position"
            },
            template="plotly_white",                # Use a clean plot theme
            text=bar_chart_metric                   # Display the metric value on the bars
        )
        # Update layout properties (axis titles, legend, height)
        fig_bar.update_layout(
            xaxis_title=bar_chart_metric_display,
            yaxis_title="Player",
            legend_title_text='Position',
            height=600
        )
        # Format the text displayed on the bars to 2 decimal places
        fig_bar.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        # Display the plot in Streamlit
        st.plotly_chart(fig_bar, use_container_width=True)
        # Add explanatory text for the chart
        st.markdown("""
        **How to Read:** This chart shows the top 15 players ranked by the selected metric (per 90 minutes).
        Longer bars indicate higher performance in that specific metric. Color indicates primary position.
        Helps quickly identify the league leaders in key statistical areas.
        """)

        # Add an expander to optionally show the underlying filtered data
        with st.expander("Show Filtered Data Table"):
             st.dataframe(df_filtered, use_container_width=True)

# Logic for "Compare Players" mode
elif analysis_mode == "Compare Players":
    st.header("Compare Players")

    # Check if there are players available after filtering
    if not player_list:
        st.warning("No players match the current filter criteria to compare.")
    else:
        # Create two columns for player selection dropdowns
        col1, col2 = st.columns(2)
        with col1:
            # Select Player 1
            player1_default_index = 0 # Default to the first player in the list
            player1 = st.selectbox("Select Player 1", player_list, index=player1_default_index, key="player1")

        with col2:
            # Create a list for Player 2 excluding Player 1
            player_list_2 = [p for p in player_list if p != player1]
            # Set a default index for Player 2, handling edge cases
            player2_default_index = 0
            if not player_list_2: player2_default_index = None # No other players available
            elif len(player_list) > 1 and player1 == player_list[0]: player2_default_index = 1 if len(player_list_2) > 0 else 0 # Default to second if p1 was first

            # Select Player 2, disable if no other players are available
            player2 = st.selectbox("Select Player 2", player_list_2, index=player2_default_index, key="player2", disabled=(not player_list_2))

        # Proceed only if two distinct players are selected
        if player1 and player2:
            # Filter the DataFrame for the two selected players
            selected_players_data = df_filtered[df_filtered['Player'].isin([player1, player2])].copy()

            # Ensure comparison columns exist in the selected data
            valid_comparison_cols = [col for col in comparison_actual_cols if col in selected_players_data.columns]
            comparison_df = selected_players_data[valid_comparison_cols]

            # Prepare table: Set Player as index and Transpose (metrics as rows)
            comparison_df = comparison_df.set_index('Player').T
            comparison_df.index.name = "Metric"            # Rename the index column
            comparison_df = comparison_df.rename(columns=str) # Ensure player names (now columns) are strings

            # Rename the metric index using the user-friendly names
            display_name_map = {v: k for k, v in comparison_cols_info.items()}
            comparison_df = comparison_df.rename(index=display_name_map)

            # Identify rows (metrics) that are likely numeric for formatting/highlighting
            rows_to_highlight = [idx for idx in comparison_df.index if any(sub in idx for sub in ['per 90', '%', 'Age', 'Min'])]

            # Display the comparison table
            st.subheader(f"Comparison: {player1} vs. {player2}")
            st.dataframe(
                comparison_df.style
                .format("{:.2f}", subset=pd.IndexSlice[rows_to_highlight,:])  # Format numeric metrics to 2 decimal places
                .highlight_max(axis=1, color='lightgreen', subset=pd.IndexSlice[rows_to_highlight,:]) # Highlight the max value in each numeric row
                , use_container_width=True
            )
            # Add explanatory text for the table
            st.markdown("""
            **How to Read:** This table compares the selected players across key metrics.
            Higher values are generally better for performance metrics (highlighted green).
            """)
        elif player1 and not player_list_2:
             # Handle case where only one player matches filters
             st.info(f"Only {player1} matches the current filters. Select another player or adjust filters.")
        else:
             # Prompt user if only one player is selected
             st.info("Select two players to compare.")


# Logic for "Analyze Opponent" mode
elif analysis_mode == "Analyze Opponent":
    st.header("Analyze Opponent")

    # Create a select box to choose the opponent team
    selected_team = st.selectbox("Select Opponent Team", all_teams, index=0)

    # Create a select box to choose the metric for sorting and highlighting threats
    threat_metric_display = st.selectbox(
        "Highlight Top Players by Metric",
        metric_display_names,
        index=metric_display_names.index('xG per 90') if 'xG per 90' in metric_display_names else 0 # Default to xG per 90
    )
    # Get the actual column name for the threat metric
    threat_metric = metric_options_dict[threat_metric_display]

    # Filter the *original* DataFrame (df) for the selected team (ignore sidebar filters here)
    opponent_df = df[df['Squad'] == selected_team].copy()

    # Check if any data exists for the selected team
    if opponent_df.empty:
        st.warning(f"No data found for team: {selected_team}")
    # Check if the chosen threat metric exists in the data
    elif threat_metric not in opponent_df.columns:
        st.warning(f"Selected highlight metric '{threat_metric_display}' not found for this team's data.")
    else:
        st.subheader(f"Player Stats for {selected_team}")
        st.write(f"Highlighting based on: {threat_metric_display}")

        # Select only the predefined columns relevant for opponent analysis
        display_cols_opponent = [col for col in opponent_analysis_cols if col in opponent_df.columns]
        opponent_df_display = opponent_df[display_cols_opponent]

        # Sort the DataFrame by the selected threat metric (descending)
        opponent_df_display = opponent_df_display.sort_values(by=threat_metric, ascending=False).reset_index(drop=True)

        # Display the table with styling
        st.dataframe(
            opponent_df_display.style
            .format("{:.2f}", subset=[col for col in display_cols_opponent if 'per90' in col]) # Format per 90 columns
            # .background_gradient(cmap='Greens', subset=[threat_metric], low=0.1) # Apply green gradient to threat metric column
            , use_container_width=True
        )
        # Add explanatory text for the table
        st.markdown("""
        **How to Read:** This table shows key statistics for all players on the selected opponent team.
        The table is sorted by the chosen **Highlight Metric** (darker green = higher value), helping identify key threats.
        Review metrics like xG, xA, Progressive Passes/Carries, and Tackles per 90 to understand player roles and impact.
        """)

# Fallback for any unexpected state
else:
    st.error("Invalid analysis mode selected.")

# Note: The Design Rationale section previously here in the sidebar has been removed.
# It should be provided as a separate document.
