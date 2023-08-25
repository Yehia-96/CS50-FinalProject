from werkzeug.utils import secure_filename
from flask import Flask, request, session, render_template, flash, redirect
from cs50 import SQL
import os 
db = SQL("sqlite:///foodie.db")

#Helps with storing the uploaded img's path 
def UploadIMG(file, foodid):
    filename = secure_filename(file.filename)
    saveFolder = os.path.join("static", "images")
    imgPath = os.path.join(saveFolder, filename)

    # Create the directory if it doesn't exist
    os.makedirs(saveFolder, exist_ok=True)

    file.save(imgPath)

    db.execute("UPDATE food SET img_path = ? WHERE id = ?", imgPath, foodid)


def apology(errorMessage):
    return render_template("apology.html", errorMessage = errorMessage)

def ItConverts(number):
    try:
        newNumber = float(number) 
        currency = "{:.2f}".format(newNumber)
        euro = "\u20AC"
        return euro + str(currency)
    except:
        print("Not a number!")
    
