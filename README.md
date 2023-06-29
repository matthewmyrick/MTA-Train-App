# Train Information App

## Summary Description
The Train Information App is a PyQt5-based application that provides real-time train arrival information using the MTA API. It displays the arrival time, delay (if any), and uncertainty status for a specific train stop. The app updates the information periodically and highlights the data based on arrival time and delay status.

## How to Use
To use the Train Information App, follow these steps:

1. Clone the repository to your local machine using the following command:
   ```
   git clone <repository-url>
   ```

2. Install the required dependencies by running the following command:
   ```
   pip install -r requirements.txt
   ```

3. Create an `.env` file in the root directory of the project with the following environment variables:
   ```
   STOP_ID=<your-stop-id>
   REFRESH_RATE=<refresh-rate-in-seconds>
   MTA_API_KEY=<your-mta-api-key>
   ```
   Replace `<your-stop-id>`, `<refresh-rate-in-seconds>`, and `<your-mta-api-key>` with your actual values.

4. Run the application using the following command:
   ```
   python main.py
   ```

5. The application will launch in full-screen mode, displaying the train information in a table. The table will be updated periodically based on the specified refresh rate.

## Example Usage
Here's an example of how to use the Train Information App:

1. Clone the repository to your local machine:
   ```
   git clone https://github.com/your-username/train-information-app.git
   ```

2. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Create an `.env` file in the root directory and set the required environment variables:
   ```
   STOP_ID=1234  # Replace with your actual stop ID
   REFRESH_RATE=60  # Replace with your desired refresh rate in seconds
   MTA_API_KEY=your-mta-api-key  # Replace with your actual MTA API key
   ```

4. Run the application:
   ```
   python main.py
   ```

5. The application will launch in full-screen mode, displaying the train information for the specified stop ID. The table will update every 60 seconds (as per the example) with the latest arrival times and delays.

---

Please make sure to replace `<repository-url>`, `<your-stop-id>`, `<refresh-rate-in-seconds>`, and `<your-mta-api-key>` with the appropriate values in the actual README file.

Feel free to customize the README further by adding additional sections or instructions as needed.
