from flask import Flask, request, session, render_template, flash, redirect
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = "secret_key"

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

db = SQL("sqlite:///foodie.db")

@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/register", methods = ["GET", "POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")
    
    else:
        username = request.form.get("username")
        password = request.form.get("password")
        confirm = request.form.get("confirm")
        firstName = request.form.get("firstname")
        lastname = request.form.get("lastname")
        role = request.form.get("role")
        usernameCheck = db.execute("SELECT * FROM users WHERE username = ?;", username)
        
        if not username:
            flash("Please provide a username")
            return redirect("/register")
        
        elif not password:
            flash("Please provide a password")
            return redirect("/register")

        elif not firstName:
            flash("Please provide your First Name")
            return redirect("/register")

        
        elif len(usernameCheck) == 1:
            flash("Username already taken")
            return redirect("/register")

        elif password != confirm:
            flash("Passwords do not match")
            return redirect("/register")

        else:
            hashed = generate_password_hash(password, "pbkdf2:sha256", 12)
            db.execute("INSERT INTO users (username, PWhash, FirstName, LastName, Role) VALUES(?,?,?,?,?);", username, hashed, firstName, lastname, role)

        if __name__ == '__main__':
          app.run(port=5000,debug=True, use_reloader=True)

        return redirect("/login")
    

@app.route("/login", methods = ["GET", "POST"])
def login():
    session.clear()
    if request.method == "POST":
      username = request.form.get("username")
      password = request.form.get("password")
    
      if username == "" or password == "":
          flash("Provide username or password")
          return redirect("/login")
      
      userdata = db.execute("SELECT * FROM users WHERE username = ?", username)
      if len(userdata) == 0:
          flash("Username is incorrect")
          return redirect("/login")
      
      password_hash = userdata[0]["PWhash"]
      if check_password_hash(password_hash, password) is False:
          flash("wrong password")
          return redirect("/login")
      else:
          session["userid"] = userdata[0]["id"]
          flash("Successful login!")
          return redirect("/")
      
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()
    return redirect("/login")
    
    



