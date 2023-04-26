# ================= Lib imports =================
try:
    import redis
except ImportError:
    print("No module named 'redis' found")

# ===============================================
redis_client = redis.Redis(host='localhost', port=8585, db=0)

def populate_test_data():
    json_data = {
"id": "1",
"ipAddress": "8.8.8.8",
"location": {
"country": "US",
"region": "California",
"city": "Mountain Viw",
"lat": 37.40599,
"lng": -122.078514,
"postalCode": "94043",
"timezone": "-07:00",
},
"domains": [
"dns1.google.com",
"dns2.google.com",
],
"as": {
"asn": 15169,
"name": "Google LLC",
"route": "8.8.8.0/24",
"domain": "https://about.google/intl/en/",
},
"isp": "Google LLC"
}

# convert the JSON data to a string
    json_string = json.dumps(json_data)

# store the string in Redis with a key
    redis_client.set("key", json_string)

# retrieve the JSON string from Redis
json_string = redis_client.get("key")

# parse the JSON string back into a dictionary
json_data = json.loads(json_string)

# print the JSON data
print(json_data)

