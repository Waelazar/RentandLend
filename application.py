import os
from cs50.sql import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp

from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from middleware.apology import apology
from middleware.login import login_required

app = Flask(__name__)



# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = "images"
ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])

Session(app)


db = SQL("sqlite:///database.db")


@app.route("/")
@login_required
def index():
        # TODO
    return render_template("index.html")



@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
        # TODO
    return render_template("profile.html")


@app.route("/edit", methods=["GET", "POST"])
def edit():
    if request.method == "POST":

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        birthday = request.form.get("birthday")
        city = request.form.get("city")
        country = request.form.get("country")

        user = db.execute("SELECT * FROM dashboard WHERE user_id = :user_id ", user_id=session["user_id"])

        if not user :

            db.execute("INSERT INTO dashboard (firstname, lastname, birthday, city, country, user_id) \
                    VALUES(:firstname, :lastname, :birthday, :city, :country, :user_id)",
                    firstname = firstname, lastname = lastname, birthday = birthday,
                    city= city, country = country, user_id=session["user_id"])

            db.execute("INSERT INTO images (data) VALUES(:image)", image = imagefile)

        else :

            db.execute("UPDATE dashboard SET firstname = :firstname, lastname = :lastname, birthday = :birthday, \
                        city = :city, country = :country , user_id= :user_id",
                        firstname = firstname, lastname = lastname, birthday = birthday,
                        city= city, country = country, user_id=session["user_id"])

            db.execute("INSERT INTO images (data) VALUES(:image)", image = imagefile)

        return redirect("/profile")
    else:
        return render_template("edit.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["password_hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")



@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":

        username = request.form.get("username")
        password = request.form.get("password")
        confirmation = request.form.get("confirmation")

        # Ensure username was submitted
        if not username:
            return apology("must provide username", 400)

        # Ensure password was submitted
        if not password:
            return apology("must provide password", 400)

        # Ensure password was submitted and the passwords matches the confirmation
        if not confirmation or confirmation != password:
            return apology("must confirm password", 400)

        # insert username and hashed password into the db
        result = db.execute("INSERT INTO users (username, password_hash) VALUES(:username, :hash)",
                            username=request.form.get("username"), hash=generate_password_hash(password))
        # check if the username is already exist in the db
        if not result:
            return apology("username already exist", 400)

        # Remember which user has registered
        session["user_id"] = result

        # Redirect user to home page
        return redirect("/")
    # User reached route via GET
    else:
        return render_template("register.html")




@app.route("/add", methods=["GET", "POST"])
@login_required
def add():
    if request.method == "POST":
        if not request.form.get("product_name") or not request.form.get("latitude") or not request.form.get("longitude") or not request.form.get("price"):
            return apology("Missing required field", 400)

        result = db.execute("INSERT INTO product (name, description, user_id, latitude, longitude, price) VALUES(:name, :description, :user_id, :latitude, :longitude, :price)",
                            name=request.form.get("product_name"),
                            description=request.form.get("product_description") or "null",
                            user_id=session.get("user_id"),
                            latitude=request.form.get("latitude"),
                            longitude=request.form.get("longitude"),
                            price=request.form.get("price"))

        if request.files.getlist("images[]"):
            # found some pictures
            product_id = result
            for image in request.files.getlist("images[]"):
                #save image
                if image.filename == "" or not allowed_file(image.filename):
                    return apology("Illegal file", 400)
                image_id = save_image(image)
                rs = db.execute("INSERT INTO product_image (product_id, image_id) VALUES (:product_id, :image_id)",
                                product_id=product_id,
                                image_id = image_id)
                if not rs:
                    return apology("Couldn't save image", 400)

        if not result:
            return apology("could not save product", 400)

        return redirect("/")
    else:
        return render_template("add.html")


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def errorhandler(e):
    """Handle error"""
    return apology(e.name, e.code)

def save_image(image):
    """
    save image and return its id
    """
    filename = secure_filename(image.filename)
    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    rs = db.execute("INSERT INTO images (path) values (:data)", data=filename)
    return rs

# listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)


if __name__ == '__main__':
    app.run()


