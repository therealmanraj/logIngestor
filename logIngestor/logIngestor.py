from flask import Flask, request, render_template, Blueprint
import sqlite3
import json
import warnings
import logging
from pymongo import MongoClient

# Ignore FutureWarnings to prevent unnecessary console output
warnings.simplefilter(action='ignore', category=FutureWarning)

# Blueprint for the logIngestor
logIngestor = Blueprint('logIngestor', __name__, url_prefix='/logIngestor', template_folder='templates', static_folder='static')

# Path to the log file
log_file_path = '/Users/manraj/Documents/GitHub/november-2023-hiring-therealmanraj/app.log'

# Configure logging settings
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)
logger.propagate = True

try:
    # Create a MongoClient instance with your MongoDB connection string
    mongo_client = MongoClient("mongodb+srv://<Username>:<Password>@<collection>.u3pnrby.mongodb.net/")
    
    # Specify the database and collection to use
    db = mongo_client["logIngestor"]
    collection = db["logs"]
except Exception as e:
    print(f"Error connecting to MongoDB: {e}")

# Configure access log settings
access_log = logging.getLogger('werkzeug')
access_log.setLevel(logging.ERROR)

# Endpoint for log ingestion
@logIngestor.route('/ingest', methods=['POST','GET'])
def ingest_log():
    if request.method == "POST":
        try:
            # Extract log data from the form
            log_data = {
                "level": request.form.get('level'),
                "message": request.form.get('message'),
                "resourceId": request.form.get('resourceId'),
                "timestamp": request.form.get('timestamp'),
                "traceId": request.form.get('traceId'),
                "spanId": request.form.get('spanId'),
                "commit": request.form.get('commit'),
                "metadata": {
                    "parentResourceId": request.form.get('parentResourceId')
                }
            }

            # Ingest log data into SQLite
            con = sqlite3.connect('ingestor.db')
            cur = con.cursor()
            json_data = json.dumps(log_data, default=str)
            cur.execute(
                '''
                INSERT INTO logTable (jsonData)
                VALUES (?)
                ''',
                (
                    json_data,
                )
            )
            con.commit()
            con.close()

            # Log the data to app.log
            logger.info(json.dumps(log_data, default=str))

            # Ingest log data into MongoDB
            collection.insert_one(log_data)

        except Exception as e:
            # Handle exceptions and provide feedback to the user
            return render_template('index.html', error=f"An error occurred: {str(e)}")

    return render_template('index.html')

# Endpoint for ingesting multiple logs
@logIngestor.route('/ingestMany', methods=['POST','GET'])
def ingest_many_logs():
    if request.method == "POST":
        try:
            data = request.form.get('log')

            # Handle different formats for multiple logs input
            if "}{" in data:
                data = data.replace('}{', '}, {')
            else:
                data = data.replace('} {', '}, {')
            data = f'[{data}]'

            # Ingest multiple logs into SQLite and MongoDB
            con = sqlite3.connect('ingestor.db')
            cur = con.cursor()
            for json_object in json.loads(data):
                logger.info(json.dumps(json_object, separators=(',', ':')))
                json_data = json.dumps(json_object, separators=(',', ':'), default=str)
                collection.insert_one(json_object)
                cur.execute(
                    '''
                    INSERT INTO logTable (jsonData)
                    VALUES (?)
                    ''',
                    (
                        json_data,
                    )
                )
            con.commit()
            con.close()

        except Exception as e:
            # Handle exceptions and provide feedback to the user
            return render_template('index.html', error=f"An error occurred: {str(e)}")

    return render_template('index.html')

# Endpoint for retrieving logs
@logIngestor.route('/extraction', methods=['GET','POST'])
def get_logs():
    filters = {}
    try:
        # Extract filters from the form
        if request.form.get('level'):
            filters["level"] = request.form.get('level')
        if request.form.get('message'):
            filters["message"] = request.form.get('message')
        if request.form.get('resourceId'):
            filters["resourceId"] = request.form.get('resourceId')
        if request.form.get('timestamp'):
            filters["timestamp"] = request.form.get('timestamp')
        if request.form.get('traceId'):
            filters["traceId"] = request.form.get('traceId')
        if request.form.get('spanId'):
            filters["spanId"] = request.form.get('spanId')
        if request.form.get('commit'):
            filters["commit"] = request.form.get('commit')
        if request.form.get('parentResourceId'):
            filters["metadata"] = {"parentResourceId": request.form.get('parentResourceId')}

        # Read all logs from the file
        with open(log_file_path, 'r') as f:
            all_logs = f.readlines()

        # Filter logs based on the criteria for log file
        filtered_logs = []
        for log in all_logs:
            try:
                log_data = json.loads(log)
            except json.JSONDecodeError:
                continue
            criteria_match = True
            for key in filters:
                if filters[key] is not None and log_data.get(key) != filters[key]:
                    criteria_match = False
                    break
            if criteria_match:
                filtered_logs.append(log_data)

        # Read all logs from the relational db
        con = sqlite3.connect('ingestor.db')
        cur = con.cursor()
        filtered_logsDB = []
        for log in cur.execute('''SELECT jsonData FROM logTable'''):
            try:
                log_data = json.loads(log[0])
            except json.JSONDecodeError:
                continue
            criteria_match = True
            for key in filters:
                if filters[key] is not None and log_data.get(key) != filters[key]:
                    criteria_match = False
                    break
            if criteria_match:
                filtered_logsDB.append(log_data)
        con.close()

        # Read all logs from the non-relational db
        cursor = collection.find(filters, {'_id': 0})
        filtered_logsMongo = list(cursor)

    except Exception as e:
        # Handle other exceptions that might occur during the process
        return render_template('index.html', error=f"An error occurred: {str(e)}")

    # Render the template with the filtered logs
    return render_template('index.html', filtered_logs=filtered_logs, filtered_logsDB=filtered_logsDB, filtered_logsMongo=filtered_logsMongo)

# Default Index Route
@logIngestor.route('/', methods=['GET', 'POST'])
def index():
    try:
        con = sqlite3.connect('ingestor.db')
        cur = con.cursor()

        # Create the 'logTable' table if it does not exist
        cur.execute('''CREATE TABLE IF NOT EXISTS logTable (
                       jsonData TEXT
                   )''')

        # Sample log data
        log_data = {
            "level": "error",
            "message": "Failed to connect to DB",
            "resourceId": "server-1234",
            "timestamp": "2023-09-15T08:00:00Z",
            "traceId": "abc-xyz-123",
            "spanId": "span-456",
            "commit": "5e5342f",
            "metadata": {
                "parentResourceId": "server-0987"
            }
        }

        # Convert the log data to a JSON string
        json_data = json.dumps(log_data, default=str)

        # Insert the sample log data into the 'logTable'
        cur.execute(
            '''
            INSERT INTO logTable (jsonData)
            VALUES (?)
            ''',
            (
                json_data,
            )
        )

        # Commit the changes and close the connection
        con.commit()
        con.close()

        # Log the sample data to app.log
        logger.info(json.dumps(log_data, default=str))

        # Insert sample data into MongoDB
        collection.insert_one(log_data)

        # Render the index template
        return render_template('index.html')

    except Exception as e:
        # Handle exceptions and provide feedback to the user
        return render_template('index.html', error=f"An error occurred: {str(e)}")

# Run the Flask app if executed directly
if __name__ == "__main__":
    logIngestor.run(debug=True, use_debugger=False, debug_pin=None)
