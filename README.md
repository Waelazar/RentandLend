# RentandLend

## Purpose:

a platform where a user can rent a product for a period of time, also can lend a product

## Problem Definition:

in only 24 hours should be ready to deploy.

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
