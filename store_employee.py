import os
import pymysql
import face_recognition
import numpy as np
import json

# Database connection
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="12345",
    database="employee_db"
)
cursor = conn.cursor()

# Main employee data directory (contains department folders)
main_folder = "employee_data"

# Iterate over department folders
for department in os.listdir(main_folder):
    department_path = os.path.join(main_folder, department)

    if os.path.isdir(department_path):  # Ensure it's a folder
        for filename in os.listdir(department_path):
            if filename.endswith((".jpg", ".png")):
                try:
                    # Extract employee name and age from filename (e.g., "John_30.jpg")
                    name, age = filename.rsplit(".", 1)[0].split("_")
                    age = int(age)

                    # Load the image and extract face encodings
                    image_path = os.path.join(department_path, filename)
                    image = face_recognition.load_image_file(image_path)
                    face_encodings = face_recognition.face_encodings(image)

                    if len(face_encodings) > 0:
                        face_encoding = json.dumps(face_encodings[0].tolist())  # Convert numpy array to JSON
                    else:
                        print(f"No face found in {filename}. Skipping.")
                        continue

                    # Insert data into MySQL
                    cursor.execute("INSERT INTO employees (name, age, department, face_encoding) VALUES (%s, %s, %s, %s)",
                                   (name, age, department, face_encoding))

                except Exception as e:
                    print(f"Error processing {filename}: {e}")

# Commit and close
conn.commit()
cursor.close()
conn.close()

print("Employee data stored successfully!")
