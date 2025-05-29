from flask import Flask, request
from flask_cors import CORS
import pandas as pd
import os
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import requests
from requests.exceptions import RequestException
from tabulate import tabulate as to_table
import warnings

warnings.filterwarnings("ignore", category=UserWarning, message="resource_tracker:.*")

app = Flask(__name__, static_url_path="/static", static_folder="static", template_folder="template")
app.secret_key = "Alexander Oluwaseun Kwesi"
CORS(app)

# Global DataFrames
df = df1 = df2 = df3 = None

# Constants
API_KEY = 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c'
CSV_PATH = r'C:/Users/alexanderkwesi/Documents/Crypto Scraper Automation App/api.csv'


def is_valid_url(url):
    parsed = urlparse(url)
    return parsed.scheme in ['http', 'https'] and parsed.netloc


def fetch_crypto_data(url):
    params = {'start': 1, 'limit': 15, 'convert': 'USD'}
    headers = {'Accept': 'application/json', 'X-CMC_PRO_API_KEY': API_KEY}
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except RequestException as e:
        return {"error": str(e)}


def df_to_html_table(dataframe):
    return to_table(dataframe, tablefmt='html', stralign='center')


@app.route('/api_runner', methods=['POST'])
def api_runner():
    global df

    json_data = request.get_json()
    url = json_data.get('url')

    if not is_valid_url(url):
        return "<div>Error: URL not recognized</div>", 400

    result = fetch_crypto_data(url)
    if "error" in result:
        return f"<div>Request Error: {result['error']}</div>", 500

    df = pd.json_normalize(result['data'])
    df['timestamp'] = pd.to_datetime('now')

    if not os.path.exists(CSV_PATH):
        df.to_csv(CSV_PATH, index=False)
    else:
        df.to_csv(CSV_PATH, mode='a', header=False, index=False)

    xml_string = df.to_xml(root_name='Cryptocurrencies', row_name='Crypto')
    soup = BeautifulSoup(xml_string, 'xml')

    table_html = '<table border="1" style="border-collapse: collapse;"><thead><tr>'
    for col in df.columns:
        table_html += f"<th>{col}</th>"
    table_html += "</tr></thead><tbody>"

    for crypto in soup.find_all('Cryptocurrencies'):
        table_html += "<tr>"
        for col in df.columns:
            val = crypto.find(col).text if crypto.find(col) else ''
            table_html += f"<td>{val}</td>"
        table_html += "</tr>"
    table_html += "</tbody></table>"

    return table_html


@app.route('/api_runner_two')
def api_runner_two():
    return df_to_html_table(df) if df is not None else ("Data not loaded", 400)


@app.route('/api_runner_three')
def api_runner_three():
    global df1
    if df is None:
        return "Data not loaded", 400

    df1 = df.copy()
    return df_to_html_table(df1)


@app.route('/api_runner_four')
def api_runner_four():
    if df1 is None:
        return "Data not processed", 400

    try:
        cols = [f'quote.USD.percent_change_{p}' for p in ['1h', '24h', '7d', '30d', '60d', '90d']]
        grouped = df1.groupby('name', sort=False)[cols].mean()
    except KeyError:
        return "Expected percent_change columns not found", 500

    return df_to_html_table(grouped)


@app.route('/api_runner_five')
def api_runner_five():
    global df2
    if df1 is None:
        return "Data not processed", 400

    cols = [f'quote.USD.percent_change_{p}' for p in ['1h', '24h', '7d', '30d', '60d', '90d']]
    df2 = df1.set_index('name')[cols].stack()

    return df_to_html_table(df2)


@app.route('/api_runner_vsix')
def api_runner_vsix():
    global df3
    if df2 is None:
        return "Data not stacked", 400

    df3 = df2.to_frame(name="values").reset_index()
    df3.rename(columns={'level_1': 'percent_change'}, inplace=True)

    mapping = {
        'quote.USD.percent_change_1h': '1h',
        'quote.USD.percent_change_24h': '24h',
        'quote.USD.percent_change_7d': '7d',
        'quote.USD.percent_change_30d': '30d',
        'quote.USD.percent_change_60d': '60d',
        'quote.USD.percent_change_90d': '90d',
    }
    df3['percent_change'] = df3['percent_change'].replace(mapping)

    return df_to_html_table(df3.head())


@app.route('/api_runner_vseven')
def api_runner_vseven():
    if df is None:
        return "Data not loaded", 400

    try:
        df_btc = df[df['name'] == 'Bitcoin'][['name', 'quote.USD.price', 'timestamp']]
    except KeyError:
        return "Bitcoin data not found", 500

    return df_to_html_table(df_btc)


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=1000)
