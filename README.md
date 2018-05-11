# RentandLend

## Purpose:

a platform where a user can rent a product for a period of time, also can lend a product

## Problem Definition:

buying a new equipments is very expensive, so borrow them for a period of time would make the life easier.
## User Stories:

1. As a user i can register to the websites
2. As a user i can log in if i already have an account.
3. As a user i can search for a specific product without log in
4. As a user i can see the price, product image, lender name and the title of the product without being logged in
5. As a lender i can edit my product
6. As a user if i clicked on the product i should see :
    + Price per day
    + The description
    + A bigger images
    + Product location with the street view
7. As a user i can chat with the lender only if i am logged in

## technology Stack:

1. **Backend:**
    + Python
    + API
    + SocketIo (Chat)
2. **Frontend:**
    + Javascript
    + google map
    + ajax /JSON
    + HTML5 / CSS3 (Bootstrap 4)
3. **Database:**
    + SQLite

### Configure python 3.6 on PyCharm

open project interpreter ``` Ctrl + Alt + S ``` and add _**venv**_

1. pip install cs50 // for the Database SQL
2. Pip Install flask // web server
3. pip install Flask_session || easy_install Flask_session
4. pip install flask_socketio

## install the requirments:

1. Activate the environment using: source venv/bin/activate ( Mac )
for windows check here http://pymote.readthedocs.io/en/latest/install/windows_virtualenv.html
2. pip3 install -r requirements.txt

## How to Run:
1. make sure you are in the root directory
2. use the command ```set FLASK_APP=application.py ``` to set the name of the flask app
3. python -m flask run

*if the chat doesn't work make sure to change the socketIo url to the Url yor are using with the port
that you are using*

## Video
there is two format for the video:
1. mp4
2. the second is tscproj (it is a Camtasia studio project), to run you have to have Camtasia program.

## Contributors
1. Wael Azar => Linkedin: https://www.linkedin.com/in/wael-azar-859576135/
2. Martin Freisehner => Xing: https://www.xing.com/profile/Martin_Freisehner

*this project was part of the CS50 course that we did.*
