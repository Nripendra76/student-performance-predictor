
from flask import Flask, render_template, request
import numpy as np
import joblib
import pyodbc

model = joblib.load("grade_prediction_model.pkl")

label_encoder = joblib.load("label_encoder.pkl")

app = Flask(__name__)

conn = pyodbc.connect(

    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=NRIPENDRA\SQLEXPRESS;'
    'DATABASE=StudentPredictionDB;'
    'Trusted_Connection=yes;'

)

cursor = conn.cursor()


@app.route('/')
def home():

    return render_template("index.html")


@app.route('/predict', methods=['POST'])
def predict():

    try:

        student_name = request.form['student_name']

        study_hours = float(request.form['study_hours'])

        attendance = float(request.form['attendance'])

        participation = float(request.form['participation'])

        engagement_score = (
            attendance * 0.4 +
            participation * 0.6
        )

        features = np.array([[
            study_hours,
            attendance,
            participation,
            engagement_score
        ]])

        prediction = model.predict(features)

        predicted_grade = label_encoder.inverse_transform(prediction)[0]

        cursor.execute('''
            INSERT INTO predictions (

                student_name,
                study_hours,
                attendance,
                participation,
                engagement_score,
                predicted_grade

            )

            VALUES (?, ?, ?, ?, ?, ?)

        ''',

            student_name,
            study_hours,
            attendance,
            participation,
            engagement_score,
            predicted_grade

        )

        conn.commit()

        return render_template(
            'index.html',
            prediction_text=f"{student_name}'s Predicted Grade is: {predicted_grade}"
        )

    except Exception as e:

        return render_template(
            'index.html',
            prediction_text=f"Error: {str(e)}"
        )


if __name__ == "__main__":

    app.run(debug=True)
