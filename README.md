# Log Ingestor

## Overview

Log Ingestor is a Flask-based web application that allows users to ingest and query logs. It supports ingesting single logs, multiple logs, and searching logs based on various criteria. The application uses SQLite for relational database storage, MongoDB for NoSQL storage, and a local log file for storing log entries.

## System Requirements

- Python 3.x
- Flask
- SQLite
- pymongo

## Installation

1. Install dependencies:

   - `pip install Flask==2.0.1`
   - `pip install pymongo==3.12.0`

2. Configure MongoDB:
   Update the MongoDB connection string in logIngestor.py with your credentials.

3. Run the application:

   Run using `python app.py`

   or

   If you are using Python 3:
   `python3 app.py`

   or

   Create a virtual environment
   `python3 -m venv venv`

   Activate the virtual environment
   `source <virtual environment directory>`

   Run the application
   `python3 app.py`

Visit http://localhost:3000 in your web browser.

## Connecting to MongoDB

To use MongoDB with this application, follow these steps to set up the connection:

1. **Create a MongoDB Atlas Account:**

   - If you don't have a MongoDB Atlas account, you can create one [here](https://www.mongodb.com/cloud/atlas).

2. **Create a Cluster:**

   - Once logged in, create a new cluster by following the instructions in the MongoDB Atlas dashboard.

3. **Get Connection String:**

   - In your cluster's dashboard, click on "Connect" to get your MongoDB connection string. Choose the appropriate connection method (e.g., "Connect Your Application").

4. **Replace Connection String in Code:**

   - In the Flask application code (`app.py`), replace the existing connection string in the `MongoClient` instantiation with your MongoDB connection string.
     ```python
     mongo_client = MongoClient("your_mongodb_connection_string_here")
     ```

5. **Configure Database and Collection:**

   - Specify the desired database and collection in the code where necessary. In the provided code, the database is set to "logIngestor" and the collection to "logs".

6. **Run the Application:**
   - Start your Flask application. The logs will be ingested into the specified MongoDB database and collection.

## Features

### Ingest Single Log:

- Navigate to the "Ingest Single Log" section.
- Fill in the log details and click "Ingest Single Log."

### Ingest Many Logs:

- Navigate to the "Ingest Many Logs" section.
- Enter logs in JSON format and click "Ingest Many Logs."

### Search Logs:

- Navigate to the "Search Logs" section.
- Fill in the search criteria and click "Search."
- Filtered logs are displayed from the log file, relational database, and MongoDB.

## Video Demonstration 

https://github.com/dyte-submissions/november-2023-hiring-therealmanraj/assets/84973062/e14b101f-3053-4628-a2f5-ce6f2358f2b1

## System Design

The system follows a modular design, with the main components being:

- app.py: Flask application setup and main entry point.
- logIngestor.py: Blueprint for log ingestion, querying, and MongoDB integration.
- templates/index.html: HTML template for the web interface.

## Features Not Implemented:

- Search within Date Ranges(While not explicitly implemented, the current structure allows for the addition of this feature)
- Regular Expressions for Search
- Combining Multiple Filters
- Real-Time Log Ingestion and Searching
- Role-Based Access
