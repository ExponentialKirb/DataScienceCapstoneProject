# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36',
                   'font-size': 40}),
    # TASK 1: Add a dropdown list to enable Launch Site selection
    # The default select value is for ALL sites
    # dcc.Dropdown(id='site-dropdown',...)
    dcc.Dropdown(
        id='site-dropdown',
        options=[{'label': 'All Sites', 'value': 'ALL'}] + [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()],
        value='ALL',
        placeholder="Select a Launch Site here",
        searchable=True
    ),
    html.Br(),
    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    # Function decorator to specify function input and output
    dcc.Graph(id='success-pie-chart'),

    # TASK 3: Add a slider to select payload range
    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-slider',
        min=min_payload,
        max=max_payload,
        step=100,
        marks={
            0: {'label': str(min_payload), 'style': {'color': '#77b0b1'}},
            2500: {'label': '2500'},
            5000: {'label': '5000'},
            7500: {'label': '7500'},
            10000: {'label': str(max_payload), 'style': {'color': '#f50'}}
        },
        value=[min_payload, max_payload]
    ),

    # TASK 4: Add a scatter chart to show the correlation between payload and launch success
    html.Div([
        dcc.Graph(id='success-payload-scatter-chart'),
    ])
])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Count success and failed launches for all sites
        all_sites_data = spacex_df['class'].value_counts().reset_index()
        all_sites_data.columns = ['class', 'count']
        fig = px.pie(all_sites_data, values='count', names='class', title='Total Success Launches for All Sites')
        return fig
    else:
        # Filter dataframe for the selected site
        selected_site_data = spacex_df[spacex_df['Launch Site'] == entered_site]['class'].value_counts().reset_index()
        selected_site_data.columns = ['class', 'count']
        fig = px.pie(selected_site_data, values='count', names='class', title=f'Success vs. Failed Launches for {entered_site}')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_chart(selected_site, payload_range):
    if selected_site == 'ALL':
        filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = 'Correlation between Payload and Success for All Sites'
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) &
                                (spacex_df['Payload Mass (kg)'] >= payload_range[0]) &
                                (spacex_df['Payload Mass (kg)'] <= payload_range[1])]
        title = f'Correlation between Payload and Success for {selected_site}'
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='class', title=title)
    fig.update_xaxes(title_text='Payload Mass (kg)')
    fig.update_yaxes(title_text='Launch Outcome (1 = Success, 0 = Failure)')
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server()