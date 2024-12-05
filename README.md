# prometheus_scrape

Script used to scrape time-series data from Prometheus.

## Setup
1. Install prometheus and node_exporter

2. Allocate resources on nodes, where you want node_exporter to run
```bash
salloc -N 1 --time=1-01:00:00 -w ares-comp-06 --exclusive
```
This command allocates node ares-comp-06 for 1 day
and 1 hour, granting exclusive access to the node for
resource monitoring.

3. Launch node_exporter on the allocated node
```bash
srun --time=24:00:00 --nodes=1 -w ares-comp-06 --exclusive --pty ./node_exporter-1.8.2.linux-amd64/node_exporter
```

4. Change `prometheus.yml` prometheus config file to ensure prometheus collects metrics from the newly added instance of node_exporter
*example of config file is in this repository, add ip addresses of new instances to `targets`*

5. After the time for which you want to collect metrics passes, launch python script
```bash
python3 script.py 
```
