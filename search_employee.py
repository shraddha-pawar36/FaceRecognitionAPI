from fastapi import FastAPI, File, UploadFile, HTTPException
import face_recognition
import numpy as np
import pymysql
import json
from PIL import Image
from io import BytesIO

app = FastAPI()

# Database connection
def get_db_connection():
    return pymysql.connect(
        host="localhost",
        user="root",
        password="12345",
        database="employee_db"
    )

@app.post("/search_employee/")
async def search_employee(file: UploadFile = File(...)):
    # Read the uploaded image
    image = Image.open(BytesIO(await file.read()))
    image = np.array(image)

    # Encode the uploaded image
    uploaded_face_encodings = face_recognition.face_encodings(image)

    if len(uploaded_face_encodings) == 0:
        raise HTTPException(status_code=400, detail="No face detected in the uploaded image.")

    uploaded_encoding = uploaded_face_encodings[0]

    # Fetch stored face encodings from the database
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, department, face_encoding FROM employees")
    employees = cursor.fetchall()

    for name, age, department, stored_encoding_json in employees:
        stored_encoding = np.array(json.loads(stored_encoding_json))

        # Compare the uploaded encoding with stored encodings
        match = face_recognition.compare_faces([stored_encoding], uploaded_encoding, tolerance=0.5)

        if match[0]:  # If True, we found a match
            return {
                "message": "Employee Found",
                "name": name,
                "age": age,
                "department": department
            }

    return {"message": "Employee not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
