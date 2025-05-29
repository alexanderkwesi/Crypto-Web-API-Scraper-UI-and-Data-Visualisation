from flask import Flask, request, json, jsonify
from flask_cors import CORS
import pandas as pd
import os
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
API_KEY = '94c85b46-dd3d-4c2b-8052-3f89e546355f'
CSV_PATH = r'C:/Users/alexanderkwesi/Documents/Crypto Scraper Automation App/api.csv'


def df_to_html_table(dataframe):
    if dataframe is None or dataframe.empty:
        return "<div>No data available</div>"
    return to_table(dataframe, tablefmt='html', stralign='center')


@app.route('/api_runner', methods=['POST', 'GET'])
def api_runner():
    global df

    json_data = request.get_json()
    if not json_data:
        return "<div>Error: No JSON payload provided</div>", 400

    # Extract parameters with defaults
    start = json_data.get("start", 1)
    limit = json_data.get("limit", 15)
    convert = json_data.get("convert", "USD")

    ##url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"
    headers = {
        'Accepts': 'application/json',
        'X-CMC_PRO_API_KEY': API_KEY
    }
    params = {
        'start': start,
        'limit': limit,
        'convert': convert
    }

    try:
        
        url = json_data.get('url')
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        result = response.json()
    except RequestException as e:
        return f"<div>Request Error: {str(e)}</div>", 500

    if 'data' not in result:
        return "<div>Error: No data in response</div>", 500

    try:
        df = pd.json_normalize(result['data'])

        # Format timestamp as ISO 8601 UTC: 2025-05-24T22:19:33Z
        df['timestamp'] = pd.to_datetime('now', utc=True).dt.strftime('%Y-%m-%dT%H:%M:%SZ')

        # Save to CSV
        if not os.path.exists(os.path.dirname(CSV_PATH)):
            os.makedirs(os.path.dirname(CSV_PATH))

        if not os.path.exists(CSV_PATH):
            df.to_csv(CSV_PATH, index=False)
        else:
            df.to_csv(CSV_PATH, mode='a', header=False, index=False)

        res_ = json.dumps(df_to_html_table(df.head()))
        return jsonify({'res_':res_})

    except Exception as e:
        return f"<div>Processing Error: {str(e)}</div>", 500


@app.route('/api_runner_two')
def api_runner_two():
    if df is None or df.empty:
        return "<div>Error: Data not loaded</div>", 400
    return df_to_html_table(df)


@app.route('/api_runner_three')
def api_runner_three():
    global df1
    if df is None or df.empty:
        return "<div>Error: Data not loaded</div>", 400

    df1 = df.copy()
    return df_to_html_table(df1)


@app.route('/api_runner_four')
def api_runner_four():
    if df1 is None or df1.empty:
        return "<div>Error: Data not processed</div>", 400

    try:
        cols = [f'quote.USD.percent_change_{p}' for p in ['1h', '24h', '7d', '30d', '60d', '90d']]
        grouped = df1.groupby('name', sort=False)[cols].mean()
        return df_to_html_table(grouped)
    except KeyError as e:
        return f"<div>Error: Missing columns - {str(e)}</div>", 500


@app.route('/api_runner_five')
def api_runner_five():
    global df2
    if df1 is None or df1.empty:
        return "<div>Error: Data not processed</div>", 400

    try:
        cols = [f'quote.USD.percent_change_{p}' for p in ['1h', '24h', '7d', '30d', '60d', '90d']]
        df2 = df1.set_index('name')[cols].stack()
        return df_to_html_table(df2)
    except KeyError as e:
        return f"<div>Error: Missing columns - {str(e)}</div>", 500


@app.route('/api_runner_six')
def api_runner_six():
    global df3
    if df2 is None:
        return "<div>Error: Data not stacked</div>", 400

    try:
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
    except Exception as e:
        return f"<div>Error: {str(e)}</div>", 500


@app.route('/api_runner_seven')
def api_runner_seven():
    if df is None or df.empty:
        return "<div>Error: Data not loaded</div>", 400

    try:
        df_btc = df[df['name'] == 'Bitcoin'][['name', 'quote.USD.price', 'timestamp']]
        if df_btc.empty:
            return "<div>Error: Bitcoin data not found</div>", 404
        return df_to_html_table(df_btc)
    except KeyError as e:
        return f"<div>Error: Missing columns - {str(e)}</div>", 500


if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1', port=5000)
