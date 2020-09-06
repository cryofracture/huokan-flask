from flask import Flask, render_template, flash, redirect, request
import uuid
from flask_bootstrap import Bootstrap
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import os
from werkzeug.security import generate_password_hash, check_password_hash



load_dotenv()
app = Flask(__name__)
boostrap = Bootstrap(app)
app.config['SECRET_KEY'] = uuid.uuid1()



@app.route('/')
def main():
    title = "New"
    return render_template('main.html', title=title)

@app.route('/generated_id', methods = ['POST', 'GET'])
def generated():
    customer_uuid   = uuid.uuid1()
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")
    customer_name   = customer_name.replace(" ", "")
    advertiser_name = advertiser_name.replace(" ", "")
    

    return render_template('generated.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name)

@app.route('/creation_confirmation', methods = ['POST'])
def confirmation():
    title           = "New Generated ID"
    customer_uuid   = request.form.get("customerID")
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    customer_name = customer_name.replace("'", "''")
    advertiser_name = advertiser_name.replace("'", "''")
    
    
    try:
        connection = psycopg2.connect(host = os.environ['DB_HOST'],
                                    port = os.environ['DB_PORT'],
                                    database = os.environ['DB_NAME'],
                                    user = os.environ['DB_USER'],
                                    password = os.environ['DB_PASS'])

        query = f""" INSERT INTO {os.environ['DB_SCHEMA']}.{os.environ['DB_TABLE']} ({os.environ['DB_COLS']}) VALUES ('{customer_uuid}','{customer_name}','{advertiser_name}','{create_date}') """

        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    #print(query)

    except psycopg2.Error as error:
        title = "Existing Customer Found"
        error = error.pgcode
        connection = psycopg2.connect(host = os.environ['DB_HOST'],
                                      port = os.environ['DB_PORT'],
                                      database = os.environ['DB_NAME'],
                                      user = os.environ['DB_USER'],
                                      password = os.environ['DB_PASS'])

        query = f""" SELECT {os.environ['TABLE_COLS']} FROM {os.environ['DB_SCHEMA']}.{os.environ['DB_TABLE']} WHERE customer_name LIKE '{customer_name}' """
        # print(query)
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
        existing_info = list(cursor.fetchone())
        customer_name = existing_info[0]
        customer_id = existing_info[1]
        created_date = existing_info[2]
        customer_name = customer_name.replace("''", "'")
        # print(existing_info[0])
        # print(existing_info[1])
        # print(existing_info[2])

        #flash('Customer already enrolled in rewards program. Please use existing ID.')

        return render_template('duplicate.html', title=title, customer_name=customer_name, customer_id=customer_id, created_date=created_date)

    #print(existing_info)
    advertiser_name = advertiser_name.replace("''", "'")
    customer_name = customer_name.replace("''", "'")

    return render_template('confirmation.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, create_date=create_date, title=title)


if __name__ == '__main__':
    app.run()#debug=os.environ['FLASK_DEBUG_STATUS'], port=os.environ['FLASK_RUN_PORT'], host=os.environ['FLASK_RUN_HOST'])