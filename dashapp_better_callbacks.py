import dash
from dash import dcc, html, dash_table, Input, Output, State
import plotly.express as px
import pandas as pd

# Load data
df = pd.read_excel("Card_list_20240709.xlsx")
df['Date Bought'] = pd.to_datetime(df['Date Bought']).dt.date
df['Profit'] = df['AVG'] - df['Price Bought']
owner_name = "Luke"

# Colors for styling
colors = {
    'background': '#111111',
    'text': 'white',
    'highlight_yellow': '#FFD700',
    'highlight_green': '#00FF00',
    'highlight_light_blue': '#ADD8E6',
}

# Initialize app
app = dash.Dash()

# App layout
app.layout = html.Div(style={'backgroundColor': colors['background'], 'margin': '10px'}, children=[
    html.H1(f"{owner_name}'s Card Collection", style={'textAlign': 'center', 'color': colors['text'], 'fontSize': '50px'}),
    html.Br(),

    # Date Picker
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div(children=[
            html.H3("Filter by Date Bought:", style={'color': colors['text']}),
            dcc.DatePickerRange(
                id='date-picker',
                start_date=df['Date Bought'].min(),
                end_date=df['Date Bought'].max(),
                display_format='DD-MM-YYYY'
            ),
        ]),
    ]),
    html.Br(),

    # Summary Text
    html.Div(style={'textAlign': 'center', 'color': colors['text']}, children=[
        html.Span([
            f"{owner_name} currently has ",
            html.Span(id='card-count', style={'color': colors['highlight_light_blue']}),
            " cards in their collection worth a total of ",
            html.Span(id='collection-value', style={'color': colors['highlight_green']}),
            "€"
        ], style={'fontSize': '20px'}),
        html.Br(),
        html.Span([
            "The most valuable card is ",
            html.Span(id='most-valuable-card', style={'color': colors['highlight_yellow']}),
            " worth approximately ",
            html.Span(id='most-valuable-price', style={'color': colors['highlight_green']}),
            "€"
        ], style={'fontSize': '20px'})
    ]),
    html.Br(),

    # Dropdown Filters
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div(children=[
            html.H3("Filter by Set Name:", style={'color': colors['text']}),
            dcc.Dropdown(
                id='set-filter',
                options=[{'label': s, 'value': s} for s in sorted(df['Set Name'].unique())],
                multi=True,
                searchable=True,
                placeholder="Select Set Name(s)"
            )
        ]),
        html.Div(children=[
            html.H3("Filter by Language:", style={'color': colors['text']}),
            dcc.Dropdown(
                id='language-filter',
                options=[{'label': l, 'value': l} for l in sorted(df['Language'].unique())],
                multi=True,
                placeholder="Select Language(s)"
            )
        ])
    ]),
    html.Br(),

    # Bar Charts
    html.Div(style={'display': 'flex', 'backgroundColor': colors['background'], 'color': colors['text']}, children=[
        html.Div(style={'width': '70%'}, children=[
            html.H2("Top 10 Sets by Volume", style={'textAlign': 'center', 'color': colors['text']}),
            dcc.Graph(id='set-bar-chart', style={'backgroundColor': colors['text']})
        ]),
        html.Div(style={'width': '30%'}, children=[
            html.H2("Cards per Language", style={'textAlign': 'center', 'color': colors['text']}),
            dcc.Graph(id='language-bar-chart', style={'backgroundColor': colors['text']})
        ])
    ]),
    html.Br(),

    # Table and Card Preview
    html.Div(style={'display': 'flex'}, children=[
        html.Div(style={'width': '70%'}, children=[
            html.H2("Full Collection", style={'textAlign': 'center', 'color': colors['text']}),
            dash_table.DataTable(
                id='card-table',
                columns=[
                    {'name': 'Card Name', 'id': 'Card Name'},
                    {'name': 'Set Name', 'id': 'Set Name'},
                    {'name': 'Language', 'id': 'Language'},
                    {'name': 'Date Bought', 'id': 'Date Bought'},
                    {'name': 'AVG', 'id': 'AVG', 'type': 'numeric'},
                    {'name': 'Profit', 'id': 'Profit', 'type': 'numeric', 'format': {'specifier': '.2f'}}
                ],
                filter_action="native",
                sort_action="native",
                page_size=50,
                row_selectable='single',
                style_table={'backgroundColor': colors['background'], 'color': colors['text']},
                style_header={'backgroundColor': colors['background'], 'color': colors['text']},
                style_cell={'backgroundColor': colors['background'], 'color': colors['text']},
                style_filter={'backgroundColor': colors['background'], 'color': colors['text']},
                style_data={'backgroundColor': colors['background'], 'color': colors['text']}        
            )
        ]),
        html.Div(style={'width': '30%', 'textAlign': 'center'}, children=[
            html.H2("Card Preview", style={'color': colors['text']}),
            html.Img(id='card-preview', style={'width': '75%', 'height': 'auto'})
        ])
    ])
])

# Callback to filter table
@app.callback(
    Output('card-table', 'data'),
    [Input('set-filter', 'value'), Input('language-filter', 'value'), Input('date-picker', 'start_date'), Input('date-picker', 'end_date')]
)
def update_filtered_table(selected_sets, selected_languages, start_date, end_date):
    filtered_df = df.copy()
    if selected_sets:
        filtered_df = filtered_df[filtered_df['Set Name'].isin(selected_sets)]
    if selected_languages:
        filtered_df = filtered_df[filtered_df['Language'].isin(selected_languages)]
    if start_date and end_date:
        filtered_df = filtered_df[(filtered_df['Date Bought'] >= pd.to_datetime(start_date).date()) &
                                  (filtered_df['Date Bought'] <= pd.to_datetime(end_date).date())]
    return filtered_df.to_dict('records')

# Callback to update bar charts
@app.callback(
    [Output('set-bar-chart', 'figure'), Output('language-bar-chart', 'figure')],
    [Input('card-table', 'data')]
)
def update_bar_charts(table_data):
    df_filtered = pd.DataFrame(table_data)
    set_chart = px.bar(df_filtered.groupby('Set Name').size().reset_index(name='Count'), x='Set Name', y='Count')
    language_chart = px.bar(df_filtered.groupby('Language').size().reset_index(name='Count'), x='Language', y='Count')
    for chart in [set_chart, language_chart]:
            chart.update_layout(
                plot_bgcolor=colors['background'],
                paper_bgcolor=colors['background'],
                font_color=colors['text'],
                xaxis=dict(showgrid=False),
                yaxis=dict(showgrid=False)
        )

    return set_chart, language_chart

# Callback to update card preview
@app.callback(
    Output('card-preview', 'src'),
    Input('card-table', 'selected_rows'),
    State('card-table', 'data')
)
def update_card_preview(selected_rows, table_data):
    if selected_rows and table_data:
        row = table_data[selected_rows[0]]
        return f"https://assets.pokemon.com/static-assets/content-assets/cms2/img/cards/web/{row['Set Code']}/{row['Set Code']}_EN_{row['Card Number']}.png"
    return ""

@app.callback(
    [Output('card-count', 'children'), Output('collection-value', 'children'), Output('most-valuable-card', 'children'), Output('most-valuable-price', 'children')],
    [Input('card-table', 'data')]
)
def update_summary_text(table_data):
    df_filtered = pd.DataFrame(table_data)
    if df_filtered.empty:
        return 0, 0, "None", 0
    return len(df_filtered), f"{df_filtered['AVG'].sum():.2f}", df_filtered.loc[df_filtered['AVG'].idxmax(), 'Card Name'], f"{df_filtered['AVG'].max():.2f}"


if __name__ == '__main__':
    app.run_server(debug=True)
