from werkzeug.utils import secure_filename
from app import db

#Helps with storing the uploaded img's path 
def UploadIMG(file, foodid):

    filename = secure_filename(file.filename)
    saveFodler = "K:\CS\Final Project\img"
    imgPath = f"{saveFodler}\{filename}"
    file.save(imgPath)

    db.execute("INSERT INTO food img_path VALUES (?) WHERE id = ?", imgPath, foodid)