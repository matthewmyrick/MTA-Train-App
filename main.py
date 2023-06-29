import sys, requests, time, os
from google.transit import gtfs_realtime_pb2
from PyQt5.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget, QHeaderView
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtCore import Qt, QTimer

STACK_LIMIT = 2
STOP_ID = "L12N"
REFRESH_RATE = 90
MTA_API_KEY = os.environ.get('MTA_API_KEY')

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
    train_dict = {}
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(response.content)
    stack = 0
    for entity in feed.entity:
        if entity.HasField('trip_update'):
            trip_update = entity.trip_update
            for stop_time_update in trip_update.stop_time_update:
                if stop_time_update.stop_id == STOP_ID and stack < STACK_LIMIT:
                    # print('Train ID:', trip_update)
                    # convert to minutes from unix epoch
                    print('Next arrival time:', (stop_time_update.arrival.time - time.time()) / 60, "minutes\n")
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

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.table = QTableWidget(self)
        self.table.setFocusPolicy(Qt.NoFocus)  # Prevent initial cell selection
        self.table.setRowCount(STACK_LIMIT)
        self.table.setColumnCount(STACK_LIMIT)
        self.table.setHorizontalHeaderLabels(['Arrival Time', 'Delay', 'Certainty'])
        self.table.setShowGrid(False)
        self.table.horizontalHeader().setHighlightSections(False)
        self.table.verticalHeader().setVisible(False)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        headerFont = QFont()
        headerFont.setPointSize(18)
        headerFont.setBold(True)
        self.table.horizontalHeader().setFont(headerFont)

        cellFont = QFont()
        cellFont.setPointSize(16)
        self.table.setFont(cellFont)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)

        self.layout = QVBoxLayout()
        self.layout.addWidget(self.table)
        self.main_widget.setLayout(self.layout)

        self.update_table()

        # Setting timer to update the table every 60 seconds
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_table)
        self.timer.start(REFRESH_RATE * 1000)

    def update_table(self):
        train_data = get_train_data()

        for i, item in train_data.items():
            if item['arrival_time'] < 1:
                arrival_time = "Now Bitch"
                color_time = QColor('red')
            else:
                arrival_time = "{:.2f}m".format(item['arrival_time'])
                if item['arrival_time'] < 3:
                    color_time = QColor('red')
                elif item['arrival_time'] < 6:
                    color_time = QColor('green')
                else:
                    color_time = QColor('black')

            if item['arrival_delay'] > 0:
                arrival_delay = "Delayed {:.2f}m".format(item['arrival_delay'] / 60)
                color_delay = QColor('orange')
            else:
                arrival_delay = "On Time"
                color_delay = QColor('black')

            if item['arrival_uncertainty'] == 0:
                arrival_uncertainty = "Good"
                color_uncertainty = QColor('black')
            else:
                arrival_uncertainty = str(item['arrival_uncertainty'])
                color_uncertainty = QColor("orange")
            
            self.table.setItem(i, 0, self.create_item(arrival_time, color_time))
            self.table.setItem(i, 1, self.create_item(arrival_delay, color_delay))
            self.table.setItem(i, 2, self.create_item(arrival_uncertainty, color_uncertainty))

        # Remove initial selection
        self.table.clearSelection()

    def create_item(self, text, color):
        item = QTableWidgetItem(text)
        item.setTextAlignment(Qt.AlignCenter)
        item.setForeground(color)
        return item

app = QApplication(sys.argv)

window = MainWindow()
window.showFullScreen()

app.exec_()
