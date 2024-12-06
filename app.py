import os
import datetime
import uuid
from flask import Flask, render_template, request, redirect, url_for, current_app
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

def create_app():
    app = Flask(__name__)
    app.config['DEBUG'] = True
    client = MongoClient(os.environ.get("MONGODB_URI"))
    app.db = client["tracker"]


    @app.context_processor
    def add_calc_date_range():
        def date_range(start: datetime.datetime):
            dates = [start + datetime.timedelta(days=diff) for diff in range(-3, 4)]
            return dates
        return {"date_range":date_range}


    def today_at_midnight():
        today = datetime.datetime.today()
        return datetime.datetime(today.year, today.month, today.day)


    @app.route("/")
    def index():
        date_str = request.args.get("date") 
        if date_str:
            selected_date = datetime.datetime.fromisoformat(date_str)
        else:
            selected_date = today_at_midnight()

        habits_on_date = list(current_app.db.habits.find({"added": {"$lte": selected_date}}))

        completions = [
            habit["habit"]
            for habit in current_app.db.completions.find({"date":selected_date})
        ]
            
        return render_template(
            "index.html",
            habits = habits_on_date,
            title = "Habit Tracker - Home",
            selected_date = selected_date,
            completions = completions
        )


    @app.route("/add", methods = ["GET","POST"])
    def add_habits():
        today = today_at_midnight()
        if request.form:
            current_app.db.habits.insert_one(
                    {"_id": uuid.uuid4().hex, "added": today, "name": request.form.get("habit")}
                ) 
        return render_template(
            "add_habits.html",
            title = "Habit Tracker - Add Habit",
            selected_date = today
        )


    @app.route("/complete", methods=["POST"])
    def complete():
        date_string = request.form.get("date")
        habit = request.form.get("habitId")
        date = datetime.datetime.fromisoformat(date_string)
        current_app.db.completions.insert_one({"date": date, "habit": habit})

        return redirect(url_for("index", date=date_string))

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
