# Import the required Libraries
import tkinter as tk
import requests, time, os
from google.transit import gtfs_realtime_pb2


def get_train_data(stack_limit=2):
    # Replace this with your actual API key
    # API_KEY = os.environ.get('MTA_API_KEY')
    # Replace this with the actual stop_id for the Grand St stop
    STOP_ID = 'L12N'

    response = requests.get(
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
        headers={'x-api-key': API_KEY},
        stream=True,
    )
    train_dict = {}
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    stack = 0
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip_update = entity.trip_update
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == STOP_ID and stack < stack_limit:
                    # print('Train ID:', trip_update)
                    # convert to minutes from unix epoch
                    print('Next arrival time:', (stop_time_update.arrival.time - time.time()) / 60)
                    train_dict[stack] = {
                        'arrival_time': (stop_time_update.arrival.time - time.time()) / 60,
                        'arrival_delay': stop_time_update.arrival.delay,
                        'arrival_uncertainty': stop_time_update.arrival.uncertainty,
                        'schedule_relationship': stop_time_update.schedule_relationship
                    }
                    stack += 1
    
    # Check if the stack is empty and add a default value
    try:
        train_dict[stack-1]
    except KeyError:
        train_dict[stack] = {
            'arrival_time': 0,
            'arrival_delay': 0,
            'arrival_uncertainty': 0,
            'schedule_relationship': 0
        }
    return train_dict

# Function to append the train data to the label
def create_train_stack():
    '''
    This function will create a stack of train data

    Returns:
        None
    '''
    # Get the train data
    train_data = get_train_data()

    # iterate through the train data and change it to the label
    for i, item in enumerate(train_data.values()):

        # update the arrival time label based on the arrival time
        if item['arrival_time'] < 1:
            tk.Label(root, text="Now Bitch").grid(row=i+1, column=0)
        else:
            tk.Label(root, text="{:.2f}m".format(item['arrival_time'])).grid(row=i+1, column=0)
            # Creating a horizontal line

        # update the arrival delay based on the delay time
        if item['arrival_delay'] > 0:
            tk.Label(root, text="Delayed by {:.2f}m".format(item['arrival_delay']/60)).grid(row=i+1, column=1)
        else:
            tk.Label(root, text="On Time").grid(row=i+1, column=1)
        
        # update the arrival uncertainty based on the value
        if item['arrival_uncertainty'] != 0:
            tk.Label(root, text="Good").grid(row=i+1, column=2)
        else:
            tk.Label(root, text=str(item['arrival_uncertainty'])).grid(row=i+1, column=2)

        # Creating a horizontal line
        tk.Frame(root, height=1, width=50, bg="black").grid(row=i+2, columnspan=3, sticky='we')


    # Call this function again after 5 seconds
    root.after(60000, create_train_stack)

# Create the main window
root = tk.Tk()

# title of train app
root.title("Train Information")

# Make the window full-screen
# root.attributes('-fullscreen', True)

# Create a label for the counter
# Header labels
tk.Label(root, text="Arrival Time").grid(row=0, column=0)
tk.Label(root, text="Delay").grid(row=0, column=1)
tk.Label(root, text="Uncertainty").grid(row=0, column=2)

# Start the counter
create_train_stack()

# Run the event loop
root.mainloop()
