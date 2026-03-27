import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Load the data
# Note: Ensure "spacex_launch_dash.csv" is in the same directory as this script
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Initialize the Dash app
app = dash.Dash(__name__)
server = app.server

# Prepare launch site options for dropdown
uniquelaunchsites = spacex_df['Launch Site'].unique().tolist()
lsites = [{'label': 'All Sites', 'value': 'All Sites'}]
for site in uniquelaunchsites:
    lsites.append({'label': site, 'value': site})

# App Layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    # TASK 1: Dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site_dropdown',
                 options=lsites,
                 placeholder='Select a Launch Site here',
                 searchable=True,
                 value='All Sites'),
    html.Br(),

    # TASK 2: Pie chart to show the total successful launches count for all sites
    # If a specific launch site was selected, show the Success vs. Failed counts for the site
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),

    # TASK 3: Slider to select payload range
    dcc.RangeSlider(
        id='payload_slider',
        min=0,
        max=10000,
        step=1000,
        marks={i: f'{i} kg' for i in range(0, 10001, 1000)},
        value=[min_payload, max_payload]
    ),

    # TASK 4: Scatter chart to show the correlation between payload and launch success
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Callback for Pie Chart
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value')]
)
def get_pie_chart(entered_site):
    if entered_site == 'All Sites':
        # Show percentage of total successes contributed by each site
        fig = px.pie(spacex_df, values='class', 
                     names='Launch Site', 
                     title='Total Success Launches By Site')
    else:
        # Show success (1) vs. failure (0) for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Group by class to count occurrences
        df_counts = filtered_df.groupby('class').size().reset_index(name='count')
        # Map 0/1 to readable labels
        df_counts['class'] = df_counts['class'].map({0: 'Failure', 1: 'Success'})
        fig = px.pie(df_counts, values='count', 
                     names='class', 
                     title=f"Total Success Launches for site {entered_site}")
    return fig

# TASK 4: Callback for Scatter Chart
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site_dropdown', component_property='value'),
     Input(component_id="payload_slider", component_property="value")]
)
def update_scattergraph(entered_site, payload_range):
    low, high = payload_range
    # Filter dataframe by payload mass range
    mask = (spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)
    filtered_df = spacex_df[mask]
    
    if entered_site == 'All Sites':
        fig = px.scatter(filtered_df, x="Payload Mass (kg)", y="class",
                         color="Booster Version",
                         title="Correlation between Payload and Success for all Sites")
    else:
        # Filter by site as well
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(site_df, x="Payload Mass (kg)", y="class",
                         color="Booster Version",
                         title=f"Correlation between Payload and Success for site {entered_site}")
    
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)