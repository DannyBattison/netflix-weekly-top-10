![Last updated](https://img.shields.io/badge/Last%20updated-2025--07--02-blue)

# Netflix Weekly Charts Scraper

## Overview
This repository automatically updates the `data` directory every Wednesday with the latest Netflix weekly charts for each country. The data is scraped from Netflix's updates, which are released every Tuesday.

## How It Works
### Scraper
A script (scraper.py) located in the src directory pulls the latest information from Netflix.

### Automation
A GitHub Action is scheduled to run the scraper script every Wednesday, then commits the data.

## Purpose
The main purpose of this repository is to provide an automated, up-to-date collection of Netflix's weekly charts, ensuring that the latest data is readily available without manual intervention.
