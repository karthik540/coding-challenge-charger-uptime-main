import sys
from collections import defaultdict

def read_input_file(file_path):
    stations = {}
    charger_reports = []
    reading_stations = False
    reading_reports = False

    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if line == "[Stations]":
                    reading_stations = True
                    reading_reports = False
                    continue
                elif line == "[Charger Availability Reports]":
                    reading_reports = True
                    reading_stations = False
                    continue

                if reading_stations and line:
                    parts = line.split()
                    station_id = int(parts[0])
                    charger_ids = list(map(int, parts[1:]))
                    for charger_id in charger_ids:
                        if charger_id in stations:
                            print("ERROR: Duplicate Charger ID", file=sys.stderr)
                            sys.exit(1)
                        stations[charger_id] = station_id

                elif reading_reports and line:
                    parts = line.split()
                    charger_id = int(parts[0])
                    start_time = int(parts[1])
                    end_time = int(parts[2])
                    status = parts[3] == 'true'
                    charger_reports.append((charger_id, start_time, end_time, status))

        return stations, charger_reports
    except Exception as e:
        print("ERROR: Invalid File Format", file=sys.stderr)
        sys.exit(1)

def calculate_uptime(stations, charger_reports):
    charger_time_spans = defaultdict(lambda: {'min': float('inf'), 'max': float('-inf'), 'up': 0})
    station_results = defaultdict(int)

    # Record time spans and up times for each charger
    for charger_id, start, end, up in charger_reports:
        charger_time_spans[charger_id]['min'] = min(charger_time_spans[charger_id]['min'], start)
        charger_time_spans[charger_id]['max'] = max(charger_time_spans[charger_id]['max'], end)
        if up:
            charger_time_spans[charger_id]['up'] += end - start

    # Calculate uptime for each station by aggregating its chargers
    for charger_id, times in charger_time_spans.items():
        station_id = stations[charger_id]
        total_time = times['max'] - times['min']
        up_time = times['up']

        if station_id not in station_results:
            station_results[station_id] = {'total': 0, 'up': 0}

        station_results[station_id]['total'] += total_time
        station_results[station_id]['up'] += up_time

    # Calculate uptime percentages for each station
    result = {}
    for station_id, times in station_results.items():
        if times['total'] > 0:
            uptime_percentage = (times['up'] * 100) // times['total']
        else:
            uptime_percentage = 0  # Handle the case where there is no data
        result[station_id] = uptime_percentage

    return result

def main():
    if len(sys.argv) != 2:
        print("ERROR: Invalid number of arguments", file=sys.stderr)
        sys.exit(1)

    file_path = sys.argv[1]
    stations, charger_reports = read_input_file(file_path)
    uptime_results = calculate_uptime(stations, charger_reports)

    for station_id in sorted(uptime_results.keys()):
        print(f"{station_id} {uptime_results[station_id]}")

if __name__ == "__main__":
    main()
