# prometheus_scrape

Script used to scrape time-series data from Prometheus.

## Setup
1. Install and run prometheus [https://prometheus.io/download/] -- check what version to install
```bash
wget https://github.com/prometheus/prometheus/releases/download/v2.53.3/prometheus-2.53.3.linux-amd64.tar.gz
tar xvfz prometheus-2.53.3.linux-amd64.tar.gz
cd prometheus-2.53.3.linux-amd64
./prometheus --config.file=./prometheus.yml
```

2. Install node_exporter [https://prometheus.io/download/#node_exporter] -- check what version to install
```bash
wget https://github.com/prometheus/node_exporter/releases/download/v<VERSION>/node_exporter-<VERSION>.<OS>-<ARCH>.tar.gz
tar xvfz node_exporter-*.*-amd64.tar.gz
cd node_exporter-*.*-amd64
```

## On Ares 
3. Allocate resources on nodes, where you want node_exporter to run
```bash
salloc -N 1 --time=1-01:00:00 -w ares-comp-06 --exclusive
```
This command allocates node ares-comp-06 for 1 day
and 1 hour, granting exclusive access to the node for
resource monitoring.

4. Launch node_exporter on the allocated node
```bash
srun --time=24:00:00 --nodes=1 -w ares-comp-06 --exclusive --pty ./node_exporter-1.8.2.linux-amd64/node_exporter
```

5. Change `prometheus.yml` prometheus config file to ensure prometheus collects metrics from the newly added instance of node_exporter
*example of config file is in this repository, add ip addresses of new instances to `targets`*
Make sure to restart prometheus after changing config file.
```bash
./prometheus --config.file=./prometheus.yml
```

7. After the time for which you want to collect metrics passes, launch python script
```bash
python3 script.py "query" "start_time" "end_time" "step"
```
Example:
```bash
python3 script.py "rate(node_disk_io_time_seconds_total[1m])" "now - 24h" "now" "60s"
```
If you want to gather data for 24 hours, you can use `"now - 24h"` as `start_time` argument. Otherwise, use unix timestamp. 
Step argument represents how often metrics need to be captured. For instance, with `step=60s`, the graph will show metrics every 1 minute.  
