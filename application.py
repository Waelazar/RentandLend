import os
from cs50.sql import SQL
# import sqlite3
from flask import Flask, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp

from werkzeug.exceptions import default_exceptions
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from middleware.apology import apology
from middleware.login import login_required

from flask_socketio import SocketIO, send
from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app)


# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


def usd(value):
    """Formats value as USD."""
    return f"${value:,.2f}"


# Custom filter
app.jinja_env.filters["usd"] = usd

# To make the usd gloabal and can use it in jinja / https://cs50.stackexchange.com/questions/24690/how-to-call-the-usd-function-in-the-jinja-template-of-quoted-html
app.jinja_env.globals.update(usd=usd)

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['UPLOAD_FOLDER'] = "static/images"
Session(app)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

db = SQL("sqlite:///database.db")


@app.route("/")
def index():
    search_term = request.args.get("search")

    if not search_term:
        main_data = db.execute(" select name, description, product.product_id, price, path from product \
                                left outer join product_image i ON product.product_id = i.product_id and i.flag_main_image=1\
                                left outer join images on images.id = i.image_id")
    else:
        main_data = db.execute(" select name, description, product.product_id, price, path from product \
                left outer join product_image i ON product.product_id = i.product_id and i.flag_main_image=1\
                left outer join images on images.id = i.image_id \
                where upper(name) like upper('%' || :search_term || '%') or upper(description) like upper('%' || :search_term || '%')",
                               search_term=search_term)
    for image in main_data:
        if image["path"] is not None:
            image["path"] = os.path.join(app.config['UPLOAD_FOLDER'], image["path"])

    return render_template("index.html", products=main_data)


@app.route("/profile", methods=["GET", "POST"])
@login_required
def profile():
    user = db.execute("SELECT * FROM dashboard"
                      " left outer join images on images.id=dashboard.image_id "
                      " WHERE user_id = :user_id ", user_id=session["user_id"])

    if not user:
        return redirect("/edit")

    for image in user:
        image["path"] = os.path.join(app.config['UPLOAD_FOLDER'], image["path"])

    return render_template("profile.html", user_data=user[0])


@app.route("/edit", methods=["GET", "POST"])
@login_required
def edit():
    if request.method == "POST":

        firstname = request.form.get("firstname")
        lastname = request.form.get("lastname")
        birthday = request.form.get("birthday")
        city = request.form.get("city")
        country = request.form.get("country")

        user = db.execute("SELECT * FROM dashboard"
                          " join images on images.id=dashboard.image_id"
                          " WHERE user_id = :user_id ", user_id=session["user_id"])

        file = request.files.get('image')
        image_id = save_image(file)

        if not user:

            db.execute("INSERT INTO dashboard (firstname, lastname, birthday, city, country, user_id, image_id) \
                    VALUES(:firstname, :lastname, :birthday, :city, :country, :user_id, :image_id)",
                       firstname=firstname, lastname=lastname, birthday=birthday,
                       city=city, country=country, user_id=session["user_id"], image_id=image_id)

        else:

            db.execute("UPDATE dashboard SET firstname = :firstname, lastname = :lastname, birthday = :birthday, \
                    city = :city, country = :country , user_id= :user_id, image_id = :image_id",
                       firstname=firstname, lastname=lastname, birthday=birthday,
                       city=city, country=country, user_id=session["user_id"], image_id=image_id)

        return redirect("/profile")
    else:
        return render_template("edit.html")


@app.route("/edit_user", methods=["GET", "POST"])
@login_required
def edit_user():
    _id = request.args.get("user_id")
    if not _id:
        return apology("must provice user id", 400)

    if request.method == "GET":
        user = db.execute("select * from dashboard"
                          " join images on images.id=dashboard.image_id"
                          " WHERE user_id = :user_id ", user_id=session["user_id"])
        if not user:
            return apology("user does not exist", 404)
        for image in user:
            image["path"] = os.path.join(app.config['UPLOAD_FOLDER'], image["path"])

        return render_template("edit.html", user=user[0])
    else:
        if not request.form.get("firstname") or not request.form.get("lastname") or not request.form.get(
                "birthday") or not request.form.get("city") or not request.form.get("country"):
            return apology("Missing required field", 400)

        image_user = db.execute("SELECT * FROM dashboard"
                                " join images on images.id=dashboard.image_id"
                                " WHERE user_id = :user_id ", user_id=session["user_id"])

        file = request.files.get('image_edit')
        if file:
            image_id = save_image(file)
            result = db.execute(
                "update dashboard set firstname=:firstname, lastname=:lastname, birthday=:birthday, city=:city,"
                " country=:country, image_id = :image_id where user_id=:user_id",
                firstname=request.form.get("firstname"),
                lastname=request.form.get("lastname") or "null",
                birthday=request.form.get("birthday"),
                city=request.form.get("city"),
                country=request.form.get("country"),
                image_id=image_id,
                user_id=_id)
        else:
            result = db.execute(
                "update dashboard set firstname=:firstname, lastname=:lastname, birthday=:birthday, city=:city,"
                " country=:country where user_id=:user_id",
                firstname=request.form.get("firstname"),
                lastname=request.form.get("lastname") or "null",
                birthday=request.form.get("birthday"),
                city=request.form.get("city"),
                country=request.form.get("country"),
                user_id=_id)
        if not result:
            return apology("Could not save product", 400)

        return redirect("/profile")


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

        # Insert username and hashed password into the db
        result = db.execute("INSERT INTO users (username, password_hash) VALUES(:username, :password_hash)",
                            username=request.form.get("username"), password_hash=generate_password_hash(password))
        # Check if the username is already exist in the db
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
        if not request.form.get("product_name") or not request.form.get("latitude") or not request.form.get("longitude") \
                or not request.form.get("location") or not request.form.get("price") or not request.files.get('image'):
            return apology("Missing required field", 400)

        result = db.execute(
            "INSERT INTO product (name, description, user_id, latitude, longitude, price, location) VALUES(:name, :description, :user_id, :latitude, :longitude, :price, :location)",
            name=request.form.get("product_name"),
            description=request.form.get("product_description") or "null",
            user_id=session.get("user_id"),
            latitude=request.form.get("latitude"),
            longitude=request.form.get("longitude"),
            location=request.form.get("location"),
            price=request.form.get("price"))

        # main image
        img = request.files.get('image')
        # found some pictures
        product_id = result
        if img:
            # save image
            if img.filename == "" or not allowed_file(img.filename):
                return apology("Illegal main file", 400)

            image_id = save_image(img)
            rs = db.execute(
                "INSERT INTO product_image (product_id, image_id, flag_main_image) VALUES (:product_id, :image_id, 1)",
                product_id=product_id,
                image_id=image_id)
        # additional images
        if request.files.getlist("images[]") and len(request.files.getlist("images[]")) >= 2:
            for image in request.files.getlist("images[]"):
                # save image
                if image.filename == "" or not allowed_file(image.filename):
                    return apology("Illegal file", 400)
                image_id = save_image(image)
                rs = db.execute("INSERT INTO product_image (product_id, image_id) VALUES (:product_id, :image_id)",
                                product_id=product_id,
                                image_id=image_id)
                if not rs:
                    return apology("Couldn't save image", 400)

        if not result:
            return apology("could not save product", 400)

        return redirect("/")
    else:
        return render_template("add.html")


@app.route("/edit_product", methods=["GET", "POST"])
@login_required
def edit_product():
    product_id = request.args.get("product_id")
    if not product_id:
        return apology("must provice product id", 400)

    if request.method == "GET":
        product = db.execute(
            "select name, description, price, longitude, latitude, location, product_id from product where product_id=:product_id and user_id=:user_id",
            product_id=product_id, user_id=session.get("user_id"))
        if not product:
            return apology("Product does not exist", 404)

        return render_template("add.html", product=product[0])
    else:
        if not request.form.get("product_name") or not request.form.get("latitude") or not request.form.get(
                "longitude") or not request.form.get("price") or not request.form.get("location"):
            return apology("Missing required field", 400)

        result = db.execute(
            "update product set name=:name, description=:description, latitude=:latitude, longitude=:longitude,"
            " price=:price, location = :location where product_id=:product_id",
            name=request.form.get("product_name"),
            description=request.form.get("product_description") or "null",
            latitude=request.form.get("latitude"),
            longitude=request.form.get("longitude"),
            price=request.form.get("price"),
            location=request.form.get("location"),
            product_id=product_id)
        if not result:
            return apology("Could not save product", 400)

        return redirect("/")


@app.route("/show", methods=["GET", "POST"])
def show():
    product_id = request.args.get("product_id")
    if not product_id:
        return apology("must provice product id", 400)

    product = db.execute("select name, description, price, product_id, latitude, longitude, location ,user_id, username\
                        from product join users on users.id=user_id where product_id=:product_id",
                         product_id=product_id)

    if not product:
        return apology("Product does not exist", 404)

    # order -> show main image first
    image_paths = db.execute("select path, flag_main_image from images "
                             " join product_image on image_id=images.id"
                             " where product_id=:product_id"
                             " order by flag_main_image desc",
                             product_id=product_id)

    messages = db.execute("select text, username, product_id, time from messages"
                          " join users on users.id=messages.user_id"
                          " where product_id=:product_id",
                          product_id=product_id)

    is_own_product = None
    if not session.get("user_id") is None:
        is_own_product = session["user_id"] == product[0]["user_id"]
    user_id = None
    if not session.get("user_id") is None:
        user_id = session["user_id"]

    return render_template("detail.html", product=product[0], product_owner=is_own_product, image_paths=image_paths,
                           user_id=user_id,
                           messages=messages)


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@socketio.on('message')
def handleMessage(msg):
    # print('Message: ' + msg["message"] + " from user " + str(msg["user_id"]))
    rs = db.execute("select username from users where id=:user_id",
                    user_id=msg["user_id"])
    if not rs:
        return
    msg["username"] = rs[0]["username"]
    msg["time"] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    send(msg, broadcast=True)
    db.execute("insert into messages(text, user_id, product_id) values (:txt,:user_id,:product_id)",
               txt=msg["message"],
               user_id=msg["user_id"],
               product_id=msg["product_id"])


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
    socketio.run(app)
