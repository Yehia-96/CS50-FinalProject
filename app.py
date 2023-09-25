from flask import Flask, request, session, render_template, flash, redirect
from cs50 import SQL
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash
from func import apology, UploadIMG, ItConverts

app = Flask(__name__)
app.secret_key = "secret_key"

app.static_url_path = '/static'
app.static_folder = 'static'

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
    rotating_images = ["placeholderpath1.jpg","placeholderpath2.jpg","placeholderpath3.jpg"]

    return render_template("index.html", images=rotating_images)

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
            flash("Please provide a username", "error")
            return redirect("/register")
        
        elif not password:
            flash("Please provide a password", "error")
            return redirect("/register")

        elif not firstName:
            flash("Please provide your First Name", "error")
            return redirect("/register")

        
        elif len(usernameCheck) == 1:
            flash("Username already taken", "error")
            return redirect("/register")

        elif password != confirm:
            flash("Passwords do not match", "error")
            return redirect("/register")

        else:
            hashed = generate_password_hash(password, "pbkdf2:sha256", 12)
            db.execute("INSERT INTO users (username, PWhash, FirstName, LastName, Role) VALUES(?,?,?,?,?);", username, hashed, firstName, lastname, role)

        if __name__ == '__main__':
          app.run(port=5000,debug=True, use_reloader=True)

        return redirect("/login")
    

@app.route("/login", methods = ["GET", "POST"])
def login():

    if request.method == "POST":
      username = request.form.get("username")
      password = request.form.get("password")
    
      if username == "" or password == "":
          flash("Provide username or password", "error")
          return redirect("/login")
      
      userdata = db.execute("SELECT * FROM users WHERE username = ?", username)
      if len(userdata) == 0:
          flash("Username is incorrect", "error")
          return redirect("/login")
      

      password_hash = userdata[0]["PWhash"]
     
      if check_password_hash(password_hash, password) is False:
          flash("Incorrect Password", "error")
          return redirect("/login")
      else:
          session["userid"] = userdata[0]["id"]
          flash("Successful login!", "success")
          session["userRole"] = userdata[0]["Role"]
          if userdata[0]["Role"] == "Supplier":
              
             supplier_info = db.execute("SELECT * FROM supplier WHERE usersid = ?", session["userid"])

             if not supplier_info:

                db.execute("INSERT INTO supplier (usersid) VALUES (?)", session["userid"])
          else:
              customer_info = db.execute("SELECT * FROM customer WHERE userid = ?", session["userid"])

              if not customer_info:
                                  
                db.execute("INSERT INTO customer (userid) VALUES (?)", session["userid"])

          return redirect("/")
    
      
       
    else:
        return render_template("login.html")

@app.route('/logout')
def logout():
    session.clear()

    return redirect("/login")
    
@app.route('/<category>', methods=["GET", "POST"])
def show_meal(category):
    if request.method == "GET":
        meals = db.execute("SELECT * FROM food WHERE Category = ?", category)
        if len(meals) == 0:
            return apology(f"No {category} data")
       
        return render_template("meal.html", meals=meals, category=category, ItConverts=ItConverts)
    else:
        itemIDToAdd = request.form.get("item_id")
        itemSellerIDToAdd = db.execute("SELECT supplierid FROM food WHERE id = ?", itemIDToAdd)
        itemCustomerIDToAdd = session["userid"]
        db.execute("INSERT INTO orders (foodid, customerid, supplierid) VALUES(?,?,?)",
                   itemIDToAdd, itemCustomerIDToAdd, itemSellerIDToAdd)
        return redirect(f"/meal/{category}")

@app.route('/profile', methods=["GET", "POST"])
def show_profile():
    if request.method == "GET":
        
        supplier_id = db.execute("SELECT id FROM supplier WHERE usersid = ?", session["userid"])[0]["id"]
        meals = db.execute("SELECT * FROM food WHERE supplierid = ?", supplier_id)
        return render_template("profile.html", meals=meals, ItConverts = ItConverts)
    else:
        itemToDelete = request.form.get("item_id")
        db.execute("DELETE FROM food WHERE id = ?", itemToDelete)
        return redirect("/profile")

@app.route('/newitem', methods=["GET", "POST"])
def newitem():
    if request.method == "GET":
        return render_template("newitem.html")
    else:
        itemTitle = request.form.get("title")
        itemDescription = request.form.get("description")
        itemPrice = request.form.get("price")
        itemImg = request.files["image"]
        itemCategory = request.form.get("category")
        supplierId = db.execute("SELECT id FROM supplier WHERE usersid = ?", session["userid"])

        if supplierId:
            supplierId = supplierId[0]["id"]
        else:
            
            db.execute("INSERT INTO supplier (usersid) VALUES (?)", session["userid"])
            supplierId = db.execute("SELECT last_insert_rowid() AS id")[0]["id"]

       
        itemAdd = db.execute("INSERT INTO food (Title, Description, Price, Category, supplierid) VALUES (?, ?, ?, ?, ?)",
                   itemTitle, itemDescription, itemPrice, itemCategory, supplierId)

        
        newItemId = db.execute("SELECT id FROM food WHERE Title = ? AND Description = ?", itemTitle, itemDescription)[0]["id"]

        
        # Debugging print statement
        print("Newly inserted item ID:", newItemId)
        print(newItemId)
        UploadIMG(itemImg, newItemId)
        return redirect("/profile")

@app.route('/orders', methods=["GET", "POST"])
def add_order():
    if request.method == "POST":
        itemId = request.form.get("item_id")
        userId = session.get("userid")
        food_item = db.execute("SELECT * FROM food WHERE id = ?", itemId)
        if not food_item:
            flash("Invalid food item selected.")
            return redirect("/orders")

       
        supplierId = food_item[0]["supplierid"]
        supplier = db.execute("SELECT * FROM supplier WHERE id = ?", supplierId)
        if not supplier:
            flash("Invalid supplier.")
            return redirect("/orders")
        
        customer = db.execute("SELECT * FROM customer WHERE userid = ?", userId)
        if not customer:
            flash("Invalid user.")
            return redirect("/orders")

        db.execute("INSERT INTO orders (foodid, customerid, supplierid) VALUES (?, ?, ?)", itemId, customer[0]["id"], supplierId)
        flash("Order placed successfully.")
        return redirect("/orders")
    else:
        if session["userRole"] == "Customer":
          customer = db.execute("SELECT * FROM customer WHERE userid = ?", session["userid"])
          currentOrders = db.execute("SELECT * FROM orders JOIN food ON orders.foodid = food.id WHERE orders.Status = 'Not Ready' AND orders.customerid = ?", customer[0]["id"])
          return render_template("orders.html", currentOrders=currentOrders)
        else:
          supplier = db.execute("SELECT * FROM supplier WHERE usersid = ?", session["userid"])
          currentOrders = db.execute("SELECT * FROM orders JOIN food ON orders.foodid = food.id WHERE orders.Status = 'Not Ready' AND orders.supplierid = ?", supplier[0]["id"])
          return render_template("orders.html", currentOrders=currentOrders)

    
@app.route('/requested_orders', methods = ["POST"])
def method_name():
    
    itemId = int(request.form.get("item_id2"))
    db.execute("UPDATE orders SET Status = 'Ready' WHERE foodid = ?", itemId)
    return redirect("/orders")
    
@app.route('/history')
def show_history():
    if session["userRole"] == "Customer":
     customerid = db.execute("SELECT id FROM customer WHERE userid = ?", session["userid"])
     history = db.execute("""SELECT food.* FROM food JOIN orders ON food.id = orders.foodid WHERE orders.customerid = ? 
      AND orders.Status = 'Ready'
      """, customerid[0]['id'])        
     return render_template("history.html", history=history, ItConverts = ItConverts)
    else:
        return apology("Access denied")
@app.route('/')
def home():
    return render_template('home.html')




