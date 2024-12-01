from flask import Flask, render_template, request

app = Flask(__name__)
app.config['DEBUG'] = True
habits = ["test habit"]

@app.route("/")
def index():
    return render_template("index.html", habits=habits, title = "Habit Tracker - Home")

@app.route("/add", methods = ["GET","POST"])
def add_habits():
    if request.method == "POST":
        habits.append(request.form.get("habit"))
    return render_template("add_habits.html", title = "Habit Tracker - Add Habit")

if __name__ == "__main__":
    app.run(debug=True)
