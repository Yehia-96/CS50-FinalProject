from werkzeug.utils import secure_filename
from flask import Flask, request, session, render_template, flash, redirect

from app import db

#Helps with storing the uploaded img's path 
def UploadIMG(file, foodid):

    filename = secure_filename(file.filename)
    saveFodler = "K:\CS\Final Project\img"
    imgPath = f"{saveFodler}\{filename}"
    file.save(imgPath)

    db.execute("INSERT INTO food img_path VALUES (?) WHERE id = ?", imgPath, foodid)

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
    
