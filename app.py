import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# load and clean data
df = pd.read_csv("netflix_titles.csv")

df_clean = df.copy()
df_clean['director'] = df_clean['director'].fillna('Unknown')
df_clean['cast'] = df_clean['cast'].fillna('Unknown')
df_clean['country'] = df_clean['country'].fillna('Unknown')

df_clean['date_added'] = df_clean['date_added'].str.strip()
df_clean['date_added'] = pd.to_datetime(df_clean['date_added'], errors='coerce')
df_clean.dropna(subset=['date_added'], inplace=True)

df_clean['year_added'] = df_clean['date_added'].dt.year
df_clean.drop_duplicates(inplace=True)

# get unique values for dropdowns
all_types = ['All'] + list(df_clean['type'].unique())
all_years = sorted(df_clean['year_added'].unique())

# create the app
app = Dash(__name__)

app.layout = html.Div([

    html.H1("Netflix Dashboard", style={'textAlign': 'center', 'color': '#E50914'}),

    html.Hr(),

    # dropdown to filter by type
    html.Label("Select Content Type:"),
    dcc.Dropdown(
        id='type-dropdown',
        options=[{'label': t, 'value': t} for t in all_types],
        value='All',
        clearable=False
    ),

    html.Br(),

    # slider to filter by year range
    html.Label("Select Year Range:"),
    dcc.RangeSlider(
        id='year-slider',
        min=int(min(all_years)),
        max=int(max(all_years)),
        step=1,
        marks={int(y): str(int(y)) for y in all_years if y % 2 == 0},
        value=[2015, int(max(all_years))]
    ),

    html.Br(),
    html.Hr(),

    # chart 1 - titles added over time
    dcc.Graph(id='line-chart'),

    # chart 2 - top countries bar chart
    dcc.Graph(id='bar-chart'),

])


# callback to update both charts based on dropdown and slider
@app.callback(
    Output('line-chart', 'figure'),
    Output('bar-chart', 'figure'),
    Input('type-dropdown', 'value'),
    Input('year-slider', 'value')
)
def update_charts(selected_type, year_range):

    # filter data
    filtered = df_clean[
        (df_clean['year_added'] >= year_range[0]) &
        (df_clean['year_added'] <= year_range[1])
    ]

    if selected_type != 'All':
        filtered = filtered[filtered['type'] == selected_type]

    # chart 1 - line chart
    year_counts = filtered['year_added'].value_counts().sort_index().reset_index()
    year_counts.columns = ['Year', 'Count']

    fig1 = px.line(year_counts, x='Year', y='Count', markers=True,
                   title='Titles Added Over Time')

    # chart 2 - top 10 countries bar chart
    top_countries = filtered['country'].value_counts().head(10).reset_index()
    top_countries.columns = ['Country', 'Count']
    top_countries = top_countries[top_countries['Country'] != 'Unknown']

    fig2 = px.bar(top_countries, x='Country', y='Count', color='Country',
                  title='Top Countries Producing Content')

    return fig1, fig2


if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=False)
