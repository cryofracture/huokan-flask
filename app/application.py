from flask import Flask, render_template, flash, redirect, request
import uuid
from flask_bootstrap import Bootstrap
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash


# Load the environment variables, this module searches for .env first, but you can directly name the file if desired.
load_dotenv()
app = Flask(__name__)
# Bootstrap is fast, light, and super customizeable. Love it.
boostrap = Bootstrap(app)

# CSRF token
app.config['SECRET_KEY'] = uuid.uuid1()



@app.route('/')
def main():
    # Home page, enter Customer name-realm and Advertiser Name-realm.
    title = "New"
    return render_template('main.html', title=title)

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
    

    return render_template('generated.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, title=title)

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

        return render_template('duplicate.html', title=title, customer_name=customer_name, customer_id=customer_id, created_date=created_date)

    advertiser_name = advertiser_name.replace("''", "'")
    customer_name = customer_name.replace("''", "'")

    return render_template('confirmation.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, create_date=create_date, title=title)


if __name__ == '__main__':
    app.run()