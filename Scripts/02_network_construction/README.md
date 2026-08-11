# Network Construction Scripts (Stage B)

Run these in order, after Stage A (01_data_ingestion) is complete.

```bash
python scripts/02_network_construction/07_build_transit_edges.py
python scripts/02_network_construction/08_snap_stops_to_walk_graph.py
python scripts/02_network_construction/09_build_multimodal_graph.py
```

Script 09 depends on outputs from both 07 and 08.

## What each script produces

| Script | Output |
|---|---|
| 07 | `data/processed/network_graph/transit_edges.csv`, `stop_headways.csv` |
| 08 | `data/processed/network_graph/stop_to_walk_node.csv` |
| 09 | `data/processed/network_graph/multimodal_graph.pickle` (the final graph) |

## Design notes

- **Representative day:** Wednesday is used to define "typical weekday
  service" rather than analyzing every calendar variant separately.
- **Time periods:** AM_PEAK (07:00-09:30), PM_PEAK (16:00-18:30), and three
  OFF_PEAK windows filling the rest of the 05:00-24:00 service day.
- **Analysis scenario:** the merged graph (script 09) uses AM_PEAK wait
  times as the default scenario -- the standard "can you get to work on
  time" accessibility question. Stops lacking AM_PEAK data fall back to
  their average wait time across whatever periods they do have.
- **Known data quirk:** 12 out of ~26,800 stop-period combinations show a
  headway of exactly 0 seconds, caused by overlapping GTFS trip variants
  scheduled to depart the same stop at the identical minute. Small enough
  to not affect results meaningfully -- worth a one-line mention in the
  report's data limitations section.
- **Ride edge aggregation:** where multiple trips share the same stop-to-stop
  pair, we take the median travel time across all of them as the
  representative in-vehicle time.

## Sanity check to try once you've built the graph

```python
import pickle
import networkx as nx

with open("data/processed/network_graph/multimodal_graph.pickle", "rb") as f:
    G = pickle.load(f)

# Try routing between any two real stop_ids from stops.txt, e.g.:
path_len = nx.shortest_path_length(
    G, "stop_<origin_stop_id>", "stop_<dest_stop_id>", weight="travel_time"
)
print(f"{path_len/60:.1f} minutes")
```
A O'Connell St -> Tallaght Village test came out at 45.9 minutes in testing,
which is a realistic Dublin Bus travel time for that route.
