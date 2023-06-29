import sys
import requests
import time
from google.transit import gtfs_realtime_pb2
from dotenv import dotenv_values
from PyQt5.QtWidgets import (
    QApplication,
    QMainWindow,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QHeaderView,
)
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer

env_vars = dotenv_values()
STACK_LIMIT = 2
STOP_ID = env_vars.get('STOP_ID')
REFRESH_RATE = int(env_vars.get('REFRESH_RATE'))
MTA_API_KEY = env_vars.get('MTA_API_KEY')

def get_train_data():
    # Replace this with your actual API key
    response = requests.get(
        'https://api-endpoint.mta.info/Dataservice/mtagtfsfeeds/nyct%2Fgtfs-l',
        headers={'x-api-key': MTA_API_KEY},
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
                if stop_time_update.stop_id == STOP_ID and stack < STACK_LIMIT:
                    train_dict[stack] = {
                        'arrival_time': (stop_time_update.arrival.time - time.time()) / 60,
                        'arrival_delay': stop_time_update.arrival.delay,
                        'arrival_uncertainty': stop_time_update.arrival.uncertainty,
                        'schedule_relationship': stop_time_update.schedule_relationship
                    }
                    stack += 1
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
    def __init__(self):
        super().__init__()

        self.table = QTableWidget(self)
        self.table.setFocusPolicy(Qt.NoFocus)
        self.table.setRowCount(STACK_LIMIT)
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Arrival Time', 'Delay', 'Certainty'])
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        headerFont = QFont()
        headerFont.setPointSize(40)
        headerFont.setBold(True)
        self.table.horizontalHeader().setFont(headerFont)
        cellFont = QFont()
        cellFont.setPointSize(40)
        self.table.setFont(cellFont)

        self.table.verticalHeader().setDefaultSectionSize(400)  # Set the default row height

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.layout.setSpacing(100)  # Adjust the spacing between rows
        self.layout.setContentsMargins(0, 0, 0, 0)  # Remove layout margins
        self.main_widget.setLayout(self.layout)

        self.update_table()

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
