from flask import Flask, request, jsonify
from pymongo import MongoClient
from datetime import datetime

# Initialize the Flask app
app = Flask(__name__)

# MongoDB connection setup
client = MongoClient("mongodb://mongo:27017/")
db = client["fitness_db"]
report_collection = db["reports"]

# Mocked Data for Testing

# Mock user data (simulating the response from user-service)
def get_user_data(user_id):
    # Mocking a user response
    return {
        "user_id": user_id,
        "name": "John Doe",
        "age": 30,
        "weight": 75
    }

# Mock meal data (simulating the response from meal-service)
def get_meal_data(user_id, start_date, end_date):
    # Mocking meal data with random calories for each day
    return [
        {"date": "2025-04-01", "calories": 600},
        {"date": "2025-04-02", "calories": 700},
        {"date": "2025-04-03", "calories": 650},
        {"date": "2025-04-04", "calories": 800},
        {"date": "2025-04-05", "calories": 750}
    ]

# Mock workout data (simulating the response from workout-service)
def get_workout_data(user_id, start_date, end_date):
    # Mocking workout data with random duration and calories burned
    return [
        {"activity": "Running", "duration": 45, "calories_burned": 400},
        {"activity": "Cycling", "duration": 30, "calories_burned": 350},
        {"activity": "Swimming", "duration": 60, "calories_burned": 500}
    ]

# Endpoint to generate a comprehensive fitness report
@app.route('/api/report', methods=['POST'])
def generate_report():
    data = request.get_json()

    if not data or 'user_id' not in data or 'start_date' not in data or 'end_date' not in data:
        return jsonify({"message": "Missing required fields"}), 400

    try:
        start_date = datetime.strptime(data['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(data['end_date'], '%Y-%m-%d')
    except ValueError:
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD."}), 400

    user_id = data['user_id']

    # Fetch mocked data for user, meal, and workout
    user_data = get_user_data(user_id)
    meal_data = get_meal_data(user_id, data['start_date'], data['end_date'])
    workout_data = get_workout_data(user_id, data['start_date'], data['end_date'])

    if not user_data or not meal_data or not workout_data:
        return jsonify({"message": "Error retrieving data."}), 500

    # Summarize the workout data (total duration and calories burned)
    total_workout_duration = sum(workout['duration'] for workout in workout_data)
    total_calories_burned = sum(workout['calories_burned'] for workout in workout_data)

    # Summarize the meal data (total calories consumed)
    total_calories_consumed = sum(meal['calories'] for meal in meal_data)

    # Prepare the comprehensive report
    report = {
        "user_id": user_id,
        "user_name": user_data.get("name"),
        "user_age": user_data.get("age"),
        "user_weight": user_data.get("weight"),
        "report_period": {
            "start_date": data['start_date'],
            "end_date": data['end_date']
        },
        "workout_report": {
            "total_duration_minutes": total_workout_duration,
            "total_calories_burned": total_calories_burned
        },
        "meal_report": {
            "total_calories_consumed": total_calories_consumed
        }
    }

    # Store the generated report in MongoDB
    report_collection.insert_one(report)

    return jsonify(report), 200


# GET report endpoint for a given user_id
@app.route('/api/report/<user_id>', methods=['GET'])
def get_report(user_id):
    # Fetch reports from the database based on user_id
    reports = list(report_collection.find({"user_id": user_id}, {"_id": 0}))

    if not reports:
        return jsonify({"message": "No reports found for the given user_id."}), 404

    return jsonify(reports), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
