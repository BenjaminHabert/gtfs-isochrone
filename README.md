# gtfs-isochrone
create isochrone travel maps from gtfs data


# Usage

- locate a folder containing GTFS data as csv files. Required are:
    - stops.txt
    
```
git clone https://github.com/BenjaminHabert/gtfs-isochrone
cd gtfs-isochrone

# create python3 virtual environment
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

python run.py prepare path/to/gtfs/folder

```


# Notes

## Dev Todo-list

- [x] prepare data once
- [x] main function with input params
- [x] initialize data based on input params
- [x] find stops and arrival times through network
- [x] build circle shapes and assemble them
- [x] build geojson
- [ ] wrap main function with an api


## initial pseudo-code algo

```
PREPARE
- add date to stoptimes using trips + calandar_dates
- walk time between all stops

INITIALIZE
- input: position, start-time, max duration -> end-time
- filter stoptimes between start-time and end-time
- filter: walk time too long
- all stops -> arrival time (walking); select where arrival < end-time

LOOP
- selected stop -> find stoptimes
    - end-time > trip-stoptime > arrival_time
- find trip:
    - first stoptime of same trip
- split stoptimes:
    - A: with selected trip, time >= first stoptime of trip
    - B: all others, kept for next loop
- from group A stoptimes:
    - drop duplicate stop: keep earliest
    - remove if > end-time
    - remove if later than existing stop (???)
- filter walk time
    - duration lower than maximum walk time possible (earliest stoptimes - end-time)
- walk from the new stops to all stops -> new arrival times
    - drop duplicate stop: keep earliest
    - remove if > end-time
    - remove if later than existing stop
- if empty: FINISHED
- else:
    - add to existing stops
    - restart loop


CONCLUDE
- we have list of (stop, shortest_arrival_time)
- create circle with walking distance for each
- add circle from start position
- merge all circles in a single shape
```
