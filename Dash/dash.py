import dash
from dash import dcc, html, Input, Output, State
import pandas as pd
import plotly.express as px
import base64
import io


# Функция для обработки загруженного файла
def parse_contents(contents):
    content_type, content_string = contents.split(',')
    decoded = base64.b64decode(content_string)
    return pd.read_csv(io.StringIO(decoded.decode('utf-8')))


app = dash.Dash(__name__)

app.layout = html.Div(style={'backgroundColor': '#f0f0f0', 'padding': '20px'}, children=[
    html.Div(style={'textAlign': 'center', 'marginBottom': '20px'}, children=[
        html.H1(children='Дашборд анализа продаж.', style={'color': '#333'}),
        html.P(children='Анализируйте данные о продажах с помощью моего дашбордов.',
               style={'fontSize': '18px', 'color': '#666'})
    ]),
    dcc.Upload(
        id='upload-data',
        children=html.Button('Загрузить CSV файл'),
        style={
            'width': '100%',
            'height': '50px',
            'lineHeight': '50px',
            'borderWidth': '1px',
            'borderStyle': 'solid',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        },
    ),

    html.Div(id='output-data-upload'),
    html.Div(style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'space-around'}, id='graphs-container')
])


# Обработчик загрузки данных
@app.callback(
    Output('graphs-container', 'children'),
    Input('upload-data', 'contents'),
    State('upload-data', 'filename'),
    prevent_initial_call=True
)
def update_graphs(contents, filename):
    df = parse_contents(contents)

    df['Дата'] = pd.to_datetime(df['Дата'])
    df.set_index('Дата', inplace=True)

    total_sales_fig = px.bar(
        df.resample('M').sum().reset_index(),
        x='Дата',
        y='Сумма',
        title='Общие продажи по месяцам',
        template='plotly_dark'
    )

    sales_by_category_fig = px.pie(
        df,
        names='Категория',
        values='Сумма',
        title='Продажи по категориям',
        template='plotly_dark'
    )

    quantity_sold_fig = px.line(
        df.resample('D').sum().reset_index(),
        x='Дата',
        y='Количество',
        title='Количество проданных товаров по датам',
        template='plotly_dark'
    )

    monthly_sales_fig = px.area(
        df.resample('M').sum().reset_index(),
        x='Дата',
        y='Сумма',
        title='Продажи по месяцам',
        template='plotly_dark'
    )

    top_products_fig = px.bar(
        df.groupby('Товар')['Количество'].sum().nlargest(5).reset_index(),
        x='Количество',
        y='Товар',
        orientation='h',
        title='Топ-5 товаров по количеству проданных единиц',
        template='plotly_dark'
    )

    graphs = [
        html.Div(style={'width': '30%', 'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
                        'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.H4('Общие продажи по месяцам', style={'textAlign': 'center'}),
            dcc.Graph(figure=total_sales_fig)
        ]),
        html.Div(style={'width': '30%', 'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
                        'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.H4('Продажи по категориям', style={'textAlign': 'center '}),
            dcc.Graph(figure=sales_by_category_fig)
        ]),
        html.Div(style={'width': '30%', 'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
                        'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.H4('Количество проданных товаров по датам', style={'textAlign': 'center'}),
            dcc.Graph(figure=quantity_sold_fig)
        ]),
        html.Div(style={'width': '30%', 'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
                        'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.H4('Продажи по месяцам', style={'textAlign': 'center'}),
            dcc.Graph(figure=monthly_sales_fig)
        ]),
        html.Div(style={'width': '30%', 'margin': '10px', 'padding': '10px', 'border': '1px solid #ccc',
                        'borderRadius': '5px', 'backgroundColor': '#fff'}, children=[
            html.H4('Топ-5 товаров по количеству проданных единиц', style={'textAlign': 'center'}),
            dcc.Graph(figure=top_products_fig)
        ]),
    ]

    return graphs


# Запуск приложения
if __name__ == '__main__':
    app.run_server(debug=True)
