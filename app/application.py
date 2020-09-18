from flask import Flask, render_template, flash, redirect, request
import uuid
from flask_bootstrap import Bootstrap
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash
import re
import hashlib
#from flask.ext.navigation import Navigation

# Load the environment variables, this module searches for .env first, but you can directly name the file if desired.
load_dotenv()
app = Flask(__name__)
# Bootstrap. Love it.
boostrap = Bootstrap(app)

# CSRF token
app.config['SECRET_KEY'] = uuid.uuid1()

@app.route('/')
def main():
    # Home page, enter Customer name-realm and Advertiser Name-realm.
    title = "New"
    return render_template('main.html', title=title, active=True)

@app.route('/generated_id', methods = ['POST', 'GET'])
def generated():
    # Generate a unique ID for the customer. Copy the names from the previous page.
    # Delete spaces from the string so names like ("Cryofracture - Area 52    ") get stripped to ("Cryofracture-Area52").
    title           = "Confirmation"
    customer_uuid   = uuid.uuid1()
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")
    customer_name   = customer_name.replace(" ", "")
    advertiser_name = advertiser_name.replace(" ", "")
    

    return render_template('generated.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, title=title, active=True)

@app.route('/creation_confirmation', methods = ['POST'])
def confirmation():
    # Again copy the UUID from the 'confirmation' page, and both names.
    # Create a timestamp in postgres 'TIMESTAMP' (timestamp without timezone) format.
    # Effectively 'escape' single quotes in the Realm Names, by doubling the single quote on insert to the database.
    title           = "New Generated ID"
    customer_uuid   = request.form.get("customerID")
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")
    create_date     = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    customer_name   = customer_name.replace("'", "''")
    advertiser_name = advertiser_name.replace("'", "''")
    
    # Sends the request for the 'new' customer to the database. If the application catches an error, in this case the customer name already existing, return the existing customer's ID.
    try:
        connection = psycopg2.connect(host          = os.environ['DB_HOST'],
                                        port        = os.environ['DB_PORT'],
                                        database    = os.environ['DB_NAME'],
                                        user        = os.environ['DB_USER'],
                                        password    = os.environ['DB_PASS'])

        query = f""" INSERT INTO {os.environ['DB_SCHEMA']}.{os.environ['DB_TABLE']} ({os.environ['DB_COLS']}) VALUES ('{customer_uuid}','{customer_name}','{advertiser_name}','{create_date}') """

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()

    except psycopg2.Error as error:
        title       = "Existing Customer Found"
        error       = error.pgcode
        connection  = psycopg2.connect(host = os.environ['DB_HOST'],
                                      port = os.environ['DB_PORT'],
                                      database = os.environ['DB_NAME'],
                                      user = os.environ['DB_USER'],
                                      password = os.environ['DB_PASS'])

        query   = f""" SELECT {os.environ['TABLE_COLS']} FROM {os.environ['DB_SCHEMA']}.{os.environ['DB_TABLE']} WHERE customer_name LIKE '{customer_name}' """
        cursor  = connection.cursor()
        
        cursor.execute(query)
        connection.commit()

        existing_info   = list(cursor.fetchone())
        customer_name   = existing_info[0]
        customer_id     = existing_info[1]
        created_date    = existing_info[2]
        customer_name   = customer_name.replace("''", "'")

        return render_template('duplicate.html', title=title, customer_name=customer_name, customer_id=customer_id, created_date=created_date, active=True)

    advertiser_name = advertiser_name.replace("''", "'")
    customer_name = customer_name.replace("''", "'")

    return render_template('confirmation.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, create_date=create_date, title=title, active=True)



@app.route('/customer/lookup', methods = ['GET'])
def lookup():
    # Lookup page, enter Customer name-realm to get existing UUID.
    title = "Customer Lookup"
    return render_template('lookup.html', title=title, active=True)

@app.route('/customer/lookup/results', methods = ['GET'])
def lookup_results():
    # Lookup page, enter Customer name-realm to get existing UUID.
    title = "Lookup Results"
    return render_template('lookup_results.html', title=title, active=True)

@app.route('/registration', methods = ['GET'])
def registration():
    # Registration page, enter Advertiser name-realm and desired password (encrypted before application sees it).
    title = "Advertiser Registration"

    return render_template('registration.html', title=title, active=True)

@app.route('/registration/confirmation', methods = ['POST'])
def registration_confirmation():
    advertiser_name = request.form.get('name')
    advertiser_email = request.form.get('email')
    password1 = request.form.get('psw')
    password2 = request.form.get('psw-repeat')
    advertiser_name = advertiser_name.replace(" ", "")
    if advertiser_email.contains("@") and advertiser_email.contains("."):
        if password1 == password2:
            pass_flag = 0
            while True:
                if(len(password)<10):
                    flag = -1
                    error = "Warning: Password too short."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                elif not re.search("[a-z]", password):
                    flag = -1
                    error = "Must contain 1 lower case."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                elif not re.search("[A-Z]", password):
                    flag = -1
                    error = "Must contain 1 upper case."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                elif not re.search("[0-9]", password):
                    flag = -1
                    error = "Must contain a number."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                elif not re.search("[_!@#$%^&*()_+-=[{\]};:'\",<.>\/\?]", password):
                    flag = -1
                    error = "Must contain a special character."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                elif re.search("\s", password):
                    flag = -1
                    error = "Cannot contain a space."
                    return redirect(url_for('registration'), title=title, active=True, error=error)
                else:
                    flag = 0
                    password            = password1.encode()
                    salt                = os.environ['SALT_PASS'].encode()
                    password_hash       = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
                    advertiser_email    = hashlib.pbkdf2_hmac("sha256", advertiser_email, salt, 100000)

                    try:
                        create_date         = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        advertiser_name     = advertiser_name.replace("'", "''")
                        advertiser_id       = uuid.uuid1()

                        connection = psycopg2.connect(host          = os.environ['DB_HOST'],
                                                        port        = os.environ['DB_PORT'],
                                                        database    = os.environ['REG_DB_NAME'],
                                                        user        = os.environ['DB_USER'],
                                                        password    = os.environ['DB_PASS'])

                        query = f""" INSERT INTO {os.environ['DB_SCHEMA']}.{os.environ['REG_TABLE']} ({os.environ['REG_COLS']}) VALUES ('{advertiser_id}','{advertiser_name}','{advertiser_email}','{create_date}', '{password_hash}') """

                        cursor = connection.cursor()
                        cursor.execute(query)
                        connection.commit()
                        return render_template(url_for('registration_confirmation'), title=title, advertiser_id=advertiser_id, advertiser_name=advertiser_name,advertiser_email=advertiser_email, create_date=create_date, password_hash=password_hash, active=True)

                    except:
                        error = "User already exists."
                        return redirect(url_for('registration'), title=title, active=True, error=error)
            
        else:
            error = "Warning: Passwords didn't match."
            return redirect(url_for('registration'), title=title, active=True, error=error)
    else:
        error = "Warning: Email must be valid email address."
        return redirect(url_for('registration'), title=title, active=True, error=error)
    return render_template('main.html', title=title, active=True)

@app.route('/login', methods = ['POST','GET'])
def login():
    # Advertiser Login Page
    title = "Advertiser Login"

    

    if request.method == "POST":
        try:
            advertiser_email = request.form.get('email')
            password = request.form.get('psw')
            password            = password.encode()
            salt                = os.environ['SALT_PASS'].encode()
            password_hash       = hashlib.pbkdf2_hmac("sha256", password, salt, 100000)
            advertiser_email    = hashlib.pbkdf2_hmac("sha256", advertiser_email, salt, 100000)
            connection = psycopg2.connect(host          = os.environ['DB_HOST'],
                                            port        = os.environ['DB_PORT'],
                                            database    = os.environ['REG_DB_NAME'],
                                            user        = os.environ['DB_USER'],
                                            password    = os.environ['DB_PASS'])

            #query = f""" INSERT INTO {os.environ['DB_SCHEMA']}.{os.environ['REG_TABLE']} ({os.environ['REG_COLS']}) VALUES ('{advertiser_id}','{advertiser_name}','{advertiser_email}','{create_date}', '{password_hash}') """
            query = f""" SELECT * FROM {os.environ['DB_SCHEMA']}.{os.environ['REG_TABLE']} WHERE advertiser_email LIKE {advertiser_email} AND WHERE advertiser_password LIKE {password_hash} """
            advertiser_info = list(cursor.fetchone())

            cursor = connection.cursor()
            cursor.execute(query)
            connection.commit()
            return render_template('login.html', active=True, title=title) #)advertiser_id=advertiser_id, advertiser_name=advertiser_name,advertiser_email=advertiser_email, create_date=create_date, password_hash=password_hash, active=True)

        except:
            #error = "Cannot contain a space."
            return redirect(url_for('registration'), title=title, active=True)


    return render_template('login.html', title=title, active=True)

# @app.route('/login/successul', methods = ['GET'])
# def redeem():
#     # Advertiser Login Successful Page
#     title = "Successful login"
#     return redirect(url_for('main'), title=title, active=True)

@app.route('/redeem', methods = ['GET'])
def redeem():
    # Point redemption page, enter Customer UUID and select point redemption reward.
    title = "Customer Redemption"
    return render_template('main.html', title=title, active=True)

@app.route('/terms', methods = ['GET'])
def terms():
    # Point redemption page, enter Customer UUID and select point redemption reward.
    title = "Huokan Rewards Terms"
    return render_template('terms.html', title=title, active=True)

if __name__ == '__main__':
    app.run()

"""
login_password = hashlib.pbkdf2_hmac(
    'sha256',
    password_to_check.encode('utf-8'), # Convert the password to bytes
    salt, 
    100000
)

"""