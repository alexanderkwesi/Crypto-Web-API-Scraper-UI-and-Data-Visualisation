# Crypto Web API Scraper UI and Data Visualisation

A data-focused web project that collects cryptocurrency information, processes it through a backend workflow and presents the results through a simple user interface.

## Why I Built It

I built this project to practise the full data flow from external source to useful output: API requests, scraping, data preparation, backend handling and user-facing visualisation.

## Features

- Collects crypto-related data from external sources
- Uses Python backend scripts for data retrieval and processing
- Presents results through an HTML interface
- Supports data analysis using Python data libraries
- Demonstrates API usage, data cleaning and visual presentation

## Tech Stack

- Python
- Flask
- Requests
- Pandas
- Matplotlib / Seaborn
- HTML
- JavaScript / Node tooling

## Project Structure

```text
backend/       Python scripts for collecting and processing data
template/      Frontend HTML template
requirements.txt
package.json
README.md
```

## Getting Started

Install Python dependencies:

```bash
pip install -r requirements.txt
```

Install Node dependencies if using the package scripts:

```bash
npm install
```

Run the backend or project script listed in `package.json`.

## What This Shows

This project demonstrates practical backend data handling, external API/scraping work, transformation logic and the ability to turn raw data into something easier to inspect.

## Future Improvements

- Add clearer API endpoint documentation
- Add tests for the data transformation logic
- Move generated/cache files out of the repo
- Add screenshots of the UI and sample visualisations
- Add environment variable examples if external API keys are introduced
