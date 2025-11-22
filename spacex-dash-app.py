# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',                                              
                                            options=[
                                                {'label': 'All Sites', 'value': 'ALL'},
                                                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                                                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                                                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                                                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'},
                                            ],
                                            value='ALL',
                                            placeholder="Select a Launch Site here",
                                            searchable=True
                                            ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider', 
                                                min=0, max=10000, step=1000, 
                                                marks={0: '0',                                                 
                                                2000: '2000', 
                                                4000: '4000', 
                                                6000: '6000', 
                                                8000: '8000', 
                                                10000: '10000'}, 
                                                value=[min_payload, max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    filtered_df = spacex_df

    # Case 1 — ALL sites
    if entered_site == 'ALL':
        data = filtered_df.groupby('Launch Site')['class'].sum().reset_index()
        fig = px.pie(
            data,
            values='class',
            names='Launch Site',
            title='Total Successful Launches by Site',
            labels={'Launch Site': 'Outcome'}
        )
        return fig

    # Case 2 — Selected site only
    else:
        # Filter by selected site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]

        # Compute success (1) and failure (0) counts
        data = site_df['class'].value_counts().reset_index()
        data.columns = ['class', 'Count']

        fig = px.pie(
            data,
            values='Count',
            names='class',
            title=f'Success vs Failure for Site: {entered_site}',
            labels={'class': 'Outcome'}
        )
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id="payload-slider", component_property="value"))
def update_scatter(entered_site, payload_range):
    # payload_range is [min_payload, max_payload]
    low, high = payload_range

    # First filter by payload range
    df_filtered = spacex_df[
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    ]

    # Case 1: ALL sites selected
    if entered_site == 'ALL':
        fig = px.scatter(
            df_filtered,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            hover_data=['Launch Site']
        )
        return fig

    # Case 2: Specific site selected
    else:
        df_site = df_filtered[df_filtered['Launch Site'] == entered_site]

        fig = px.scatter(
            df_site,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}',
            hover_data=['Launch Site']
        )
        return fig
        
# Run the app
if __name__ == '__main__':
    app.run()
