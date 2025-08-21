from flask import Blueprint, render_template, request, redirect
import os

upload_bp = Blueprint('upload', __name__, template_folder='templates')

UPLOAD_FOLDER = os.path.join(os.getcwd(), "data")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@upload_bp.route('/upload', methods=['GET', 'POST'])
def upload():
    if request.method == "POST":
        if "file" not in request.files:
            print("No file part")
            return redirect(request.url)

        files = request.files.getlist("file")  # get all uploaded files
        saved_files = []

        for file in files:
            if file.filename == "":
                continue  # skip empty fields

            if file and file.filename.lower().endswith(".json"):
                # save each file, overwriting with the same name each time
                filepath = os.path.join(UPLOAD_FOLDER, file.filename)
                file.save(filepath)
                saved_files.append(file.filename)
            else:
                print(f"Invalid file type: {file.filename}")

        if saved_files:
            print(f"Uploaded: {', '.join(saved_files)}")
        else:
            print("No valid JSON files uploaded")

        return redirect(request.url)
    return render_template('upload.html')