"""
No ML training needed for this version:
the benchmark data (avg price per m² per city) IS the model.

This script validates the CSV and prints a summary report.
Run: python train_model.py
"""
import csv
import statistics

DATA_PATH = "data/city_price_benchmark.csv"

def validate():
    prices = []
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            prices.append(float(row["avg_price_m2"]))

    print(f"✅ Dataset loaded: {len(prices)} cities")
    print(f"   Min  : {min(prices):.0f} €/m²")
    print(f"   Max  : {max(prices):.0f} €/m²")
    print(f"   Mean : {statistics.mean(prices):.0f} €/m²")
    print(f"   Median: {statistics.median(prices):.0f} €/m²")
    print("\nNo training step required — benchmark data is the model.")

if __name__ == "__main__":
    validate()
