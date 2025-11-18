# Coding Activities

This repository contains solutions for two activities:

- Activity 1: OpenWeather CLI (`weather_cli.py`)
- Activity 2: Median with custom sort (`median.py`)

## Requirements
- Python 3.8+
- pip

Install dependencies:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r .\requirements.txt
```

## Activity 1: OpenWeather CLI
Command-line app to search current weather, manage favourites (max 3, in-memory), list favourites with live weather, and update favourites.

### Configure API key
Place a `.env` file in this folder with:
```
OPENWEATHER_API_KEY=bd5e378503939ddaee76f12ad7a97608
```
The app auto-loads `.env`. You may also export the variable in your shell instead of using `.env`.

### Run
```powershell
python .\weather_cli.py
```
Follow the menu to search/add/list/update favourites.

## Activity 2: Median with custom sort
Implements `sort(numbers)` using insertion sort and `sortAndFindMedian(numbers)` per pseudocode. Accepts CLI args or interactive input.

### Run
With numbers as arguments:
```powershell
python .\median.py 3 1 4 1 5
```
Interactive:
```powershell
python .\median.py
# Enter: 3, 1, 4, 1, 5
```
