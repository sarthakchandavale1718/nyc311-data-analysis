#!/usr/bin/env bash
# Reproduce the whole project: download, clean, analyse.
set -e
pip install -r requirements.txt
cd task1-data-cleaning && python clean_nyc311.py && cd ..
cp task1-data-cleaning/nyc311_cleaned.csv task2-eda/
cd task2-eda && python eda_nyc311.py nyc311_cleaned.csv && cd ..
echo "Done. Open task3-dashboard/dashboard.html and load task1-data-cleaning/nyc311_cleaned.csv"
