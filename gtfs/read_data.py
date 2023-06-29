import csv

def find_stop_id(stop_name):
    with open('stops.txt', 'r') as f:
        reader = csv.DictReader(f)
        print(f"READER: {reader}")
        for row in reader:
            if stop_name in row['stop_name']:
                print('Stop ID:', row['stop_id'])
                print('Stop Name:', row['stop_name'])

find_stop_id('Grand St')
