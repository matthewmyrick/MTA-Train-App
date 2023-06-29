import sys, requests, time
from google.transit import gtfs_realtime_pb2
from dotenv import dotenv_values
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer

env_vars = dotenv_values()
STACK_LIMIT = 2
STOP_ID = env_vars.get('STOP_ID')
REFRESH_RATE = env_vars.get('REFRESH_RATE')
MTA_API_KEY = env_vars.get('MTA_API_KEY')

def get_train_data():
    '''
    This function will get the train data from the MTA API
    
    Returns:
        train_dict (dict): A dictionary of train data
    '''
    # Replace this with your actual API key
    response = requests.get(
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
        headers={'x-api-key': MTA_API_KEY},
        stream=True,
    )
    # parse feed
    train_dict = {}
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    # start stack at 0
    stack = 0
    # iterate through feed
    for entity in feed.entity:
        # check if entity has trip_update data
        if entity.HasField('trip_update'):
            trip_update = entity.trip_update
            # check if trip_update has stop_time_update data
            for stop_time_update in trip_update.stop_time_update:
                # check if stop_time_update has stop_id data
                if stop_time_update.stop_id == STOP_ID and stack < STACK_LIMIT:
                    # convert to minutes from unix epoch
                    print('Next arrival time:', (stop_time_update.arrival.time - time.time()) / 60, "minutes\n")
                    # add data to dictionary
                    train_dict[stack] = {
                        'arrival_time': (stop_time_update.arrival.time - time.time()) / 60,
                        'arrival_delay': stop_time_update.arrival.delay,
                        'arrival_uncertainty': stop_time_update.arrival.uncertainty,
                        'schedule_relationship': stop_time_update.schedule_relationship
                    }
                    # increment stack
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

class MainWindow(QMainWindow):
    '''
    This class will create the main window for the application
    
    Args:
        QMainWindow (QMainWindow): The main window for the application
        
    Returns:
        None
    '''

    def __init__(self):
        '''
        This function will initialize the main window
        
        Returns:
            None
        '''
        # Initialize the main window
        super().__init__()

        # Set the window title
        self.table = QTableWidget(self)

        # Prevent initial cell selection
        self.table.setFocusPolicy(Qt.NoFocus)

        # set the number of rows and columns  
        self.table.setRowCount(STACK_LIMIT)
        self.table.setColumnCount(3)

        # set the table headers
        self.table.setHorizontalHeaderLabels(['Arrival Time', 'Delay', 'Certainty'])

        # set the table properties
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        # set the fonts of the table
        headerFont = QFont()
        headerFont.setPointSize(18)
        headerFont.setBold(True)
        self.table.horizontalHeader().setFont(headerFont)
        cellFont = QFont()
        cellFont.setPointSize(16)
        self.table.setFont(cellFont)
        
        # set the window title
        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        # set the layout of the window
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.main_widget.setLayout(self.layout)

        # Update the table
        self.update_table()

        # Setting timer to update the table every 60 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(REFRESH_RATE * 1000)

    def update_table(self):
        '''
        This function will update the table with the train data
        
        Returns:
            None
        '''
        # Get the train data
        train_data = get_train_data()

        # Update the table by iterating through the train data
        for i, item in train_data.items():
            # if the train is on time, set the color to black
            if item['arrival_time'] < 1:
                arrival_time = "Now Bitch"
                color_time = QColor('red')
            # otherwise set them the to proper colors
            else:
                # set the arrival time format
                arrival_time = "{:.2f}m".format(item['arrival_time'])
                # if arrival time less than 3 set it to red
                if item['arrival_time'] < 3:
                    color_time = QColor('red')
                # if the arrival time is less than 7 set it to green
                elif item['arrival_time'] < 7:
                    color_time = QColor('green')
                # otherwise set to black
                else:
                    color_time = QColor('black')
            # if arrival delay is > 0 set to 0 otherwise make it black and say On Time
            if item['arrival_delay'] > 0:
                arrival_delay = "Delayed {:.2f}m".format(item['arrival_delay'] / 60)
                color_delay = QColor('orange')
            else:
                arrival_delay = "On Time"
                color_delay = QColor('black')

            # if arrival uncertainty is 0 set to Good otherwise set to orange
            if item['arrival_uncertainty'] == 0:
                arrival_uncertainty = "Good"
                color_uncertainty = QColor('black')
            else:
                arrival_uncertainty = str(item['arrival_uncertainty'])
                color_uncertainty = QColor("orange")

            # set the table items based on the data and colors
            self.table.setItem(i, 0, self.create_item(arrival_time, color_time))
            self.table.setItem(i, 1, self.create_item(arrival_delay, color_delay))
            self.table.setItem(i, 2, self.create_item(arrival_uncertainty, color_uncertainty))

        # Remove initial selection
        self.table.clearSelection()

    def create_item(self, text, color):
        # Create a table item with the given text and color
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(color)
        return item

# Create the application
app = QApplication(sys.argv)

# Create the main window
window = MainWindow()
# Set the window to full screen
window.showFullScreen()

# Run the application
app.exec_()
