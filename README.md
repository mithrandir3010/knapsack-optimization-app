# Market Shopping Optimization App

This project is a desktop application that solves a bounded knapsack optimization problem for market shopping scenarios.  
Users can select products, set quantities and importance scores, and find the best combination under a given budget.

## Features

- Loads products from `items.csv`
- Automatically displays products at startup
- Search/filter products by name
- Keeps selected products in a persistent cart panel
- Shows cart total in real time
- Lets users set desired quantity and importance score per product
- Runs bounded knapsack optimization with Dynamic Programming
- Displays detailed result summary in a separate popup
- Lists products excluded from the final optimal solution
- Provides optional step-by-step algorithm process details in a separate window

## Tech Stack

- Python 3
- CustomTkinter (modern dark UI)
- CSV data source
- Dynamic Programming

## Installation

Install dependency:

```bash
python3 -m pip install --user customtkinter
```

## Run

```bash
python3 main.py
```

## Project Structure

```text
main.py        # UI, cart state, search, result and process windows
algorithm.py   # Bounded knapsack solver
data.py        # CSV loading and emoji enrichment
items.csv      # Product dataset (name, price, importance)
README.md
```