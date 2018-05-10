# Rent and Lend design
* The platform design using bootstrap 4 with some animation provided to the logo and some buttons.
* I choose to create some effects to make the platform more user interface friendly
* I tried to make the user experience as friendly and easy to the user as i can.
* 
## 1. Index
once the guest go to the website, this page will show up.
it will show the header background image, also the guest can scroll down or click view the products button to see all the products.
In the navbar the guest can register or login (if he/she has an account before).
* each product has a (title, price and a more info link to the **details page**)
* you will see a cool animate if you hover the image
* its used grid system from bootstrap 4 to display the products next to each other
* this page is linked with most pages, (**_profile, login, register, add product, show page_**)
* a guest can't see the **profile** and **add** buttons in the navbar if he/she didn't login
* the user can search on specific product using the search field, can searching with title or description

## 2. Register
In **the Register page** , i choose products image in the background with different effects when hovering on the button
or on the Logo, 
once a guest register it saves his/her data (username, crypto password )in the database.

_The configuration of the Register is the same like pset7 (**finance**)_

## 3. Login
A user can login from this page, once the user type his/her username and password, the data goes to the backend
and check if the data were correct.
1. if the data were correct then the user will redirected to the **Index page**
2. if the data weren't correct then the user will redirected to the **Apology page**

_the configuration of the Login is the same like pset7 (**finance**)_

## 4. Profile
**The Profile page**is where the user data such as (firstname, lastname, etc...) is, it designed like a card,
the user can't edit the his/her data before clicking the ``` Edit ``` button,

once the user clicked the Edit button will redirect to the **Edit Page**

## 5. Edit
**The Edit page**is where the user can edit his/her data, after the user redirected to this page, his/her
data will display and then the user can easily change. (all the field are required)

If the user wants to change the image he/she can easily click on the image and upload the new one, once 
he/she uplodaed it, the new image will display immediately _( a javascript function exist in the ```edit.html``` page is taking care of that )_ 

If the user doesn't has an account before then there is no old data to display
## 6. Add
A user can't access to the **Add page** if he/she isn't Logged in, so first the user has to be logged in.
then from the **Index page** in the navbar can click add button then will redirect the user to the **Add page**.

In the **Add page** the user can add the product information provided with the location of the product,
by putting the marker on somewhere on google map, automatically will fill the inputs of the coordinate.
also the user can add the exact address by just typing it.

About uploading images:
* The user should upload the main, this one will display in the **Index page**
* The user can upload sub-images but its not required, the sub-images will be showed in the **Details page**
with in a slider 
* The images that the user uploaded will be saved locally but also with an ```id and path```in the database
connected with product_image 
and i can know the main image from the sub-images using ```flag_main_image``` field in product_image table

## 7. Edit_product
**Edit_Product Page**, is basically the same like add however is for existing products, and only the user how own
the product can edit it,
also once the user click edit product from the **Details page**, all the product information will be 
retrieved and displayed - except the images - so can the user easily edit his/her product.

## 8. Details
In the **Details page**, there are many things to talk about:
1. The slider:
    * first image displayed in the slider is the main image
    * you can change the images by clicking left or right sign
    
2. Google map: __google map has two feature in this platform__
    * google map for the location of the user
    * the street view where is the location of the product
    * _(i choose to create street view so the renter can recognise the place if he/she went there)_
    * _using Jquery can switch between Product images and Google map_
3. Product data retrieved from the database and displayed along with the firstname of the username who 
own the product
4. the user whom owned the product should see a button called ```Edit product```, once he/she clicked
will be redirected to the **Edit_Product page**

5. The most interesting part is the chat, where is guest like the product and wants to buy it
then he/she should log in first to be able to talk with the product owner or at least to write something in the chat.

the chat uses **SocketIo**, and will display (first name, sending message time and the massege), 
also the message will be saved in the database (message table) connected with the user data

 **NOTE: if the user isn't logged in, then he/she can't type in the chat**
 
## 9. Apology
Every error like (__Not found, access denied or Invalid username or password__) will redirect to this page.

__It has been configured like the pset7 (**finance**).__

## 10. Map.hmtl
there is NO **map page**, however the ```map.html``` is where the google map written in javascript
except the street view, it's written in the ```details.html```

#11. Layout.html
the Layout.html is where the navbar is.