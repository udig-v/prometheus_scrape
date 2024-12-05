import requests
import pandas as pd
import matplotlib.pyplot as plt
import time
import argparse
import datetime

PROMETHEUS_URL = "http://localhost:9090/api/v1/query_range"

def fetch_prometheus_data(query, start, end, step):
    """Fetch data from Prometheus using HTTP API."""
    params = {
        "query": query,
        "start": start,
        "end": end,
        "step": step,
    }
    response = requests.get(PROMETHEUS_URL, params=params)
    if response.status_code == 200:
        return response.json()
    else:
        print(f"Error fetching data: {response.status_code}")
        return None

def save_to_csv(data, filename):
    """Save Prometheus data to CSV with timestamp handling."""
    if not data or "data" not in data:
        print("No data to save.")
        return
    results = data["data"]["result"]
    rows = []

    for result in results:
        metric = result["metric"]
        values = result["values"]
        for value in values:
            timestamp, val = value
            rows.append([timestamp, metric.get("instance", ""), val])

    df = pd.DataFrame(rows, columns=["timestamp", "instance", "value"])

    # Convert timestamp to datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")

    # Convert 'value' column to numeric, coercing errors to NaN
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Drop rows where 'value' is NaN    
    df = df.dropna(subset=["value"])

    # Aggregate by timestamp and instance, averaging values for duplicate timestamps
    df = df.groupby(["timestamp", "instance"], as_index=False).agg({"value": "mean"})

    df.to_csv(filename, index=False)
    print(f"Data saved to {filename}")

def plot_data(filename, output_file, query):
    """Plot the data from CSV."""
    df = pd.read_csv(filename)

    # Convert 'timestamp' column to datetime
    df['timestamp'] = pd.to_datetime(df['timestamp'])

    # Drop duplicates based on timestamp and instance
    df = df.drop_duplicates(subset=["timestamp", "instance"])

    plt.figure(figsize=(10, 6))
    for instance in df["instance"].unique():
        instance_data = df[df["instance"] == instance]
        plt.plot(instance_data["timestamp"], instance_data["value"], label=instance)

    plt.xlabel("Time")
    plt.ylabel(query.replace('_', ' '))
    plt.title(f"{query.replace('_', ' ')} Over Time")
    plt.legend()
    plt.grid(True)
    plt.gca().xaxis.set_major_locator(plt.MaxNLocator(10))  # Show up to 10 x-ticks
    plt.gca().xaxis.set_major_formatter(plt.matplotlib.dates.DateFormatter('%Y-%m-%d %H:%M:%S'))
    plt.xticks(rotation=45)

    # Automatically format the x-axis for datetime
    plt.gcf().autofmt_xdate()
    plt.tight_layout()
    plt.savefig(output_file)
    print(f"Graph saved to {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Fetch and plot Prometheus query data.")
    parser.add_argument("query", type=str, help="Prometheus query to execute.")
    parser.add_argument("start_time", type=str, help="Start time in UNIX timestamp or 'now - 24h'.")
    parser.add_argument("end_time", type=str, help="End time in UNIX timestamp or 'now'.")
    parser.add_argument("step", type=str, help="Step interval in seconds (ex. '60s').")

    args = parser.parse_args()
    
    # Parse time arguments
    if args.start_time.lower() == "now - 24h":
        start_time = int(time.time()) - 86400
    else:
        start_time = int(args.start_time)

    if args.end_time.lower() == "now":
        end_time = int(time.time())
    else:
        end_time = int(args.end_time)

    query = args.query.replace(' ', '_')
    timestamp_suffix = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    csv_filename = f"{query}_{timestamp_suffix}.csv"
    graph_filename = f"{query}_{timestamp_suffix}.svg"

    data = fetch_prometheus_data(args.query, start_time, end_time, args.step)
    save_to_csv(data, csv_filename)
    plot_data(csv_filename, graph_filename, args.query)

if __name__ == "__main__":
    main()