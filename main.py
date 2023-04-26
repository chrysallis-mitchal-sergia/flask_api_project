# ================= Lib imports =================
try:
    from flask import Flask
except ImportError:
    print("No module named 'flask' found")

try:
    from populate_test_data import populate_test_data
except ImportError:
    print("No module named 'redis' found")

# ===============================================
populate_test_data()


# =================== Endpoints mapping ===================
@app.route('/')
def hello():
    return 'Hello, World!'

@app.route('/ip-info')
# GET IP address data

@app.route('/report-abuse')
# Create IP abuse records

@app.route('/all-abuse-records')
# GET all records


# =========================================================

# Test data


# Create a Flask app: Create a new Flask app by instantiating the `Flask` class:
app = Flask(__name__)

if __name__ == '__main__':
    print('Server is running..')
    app.run()

