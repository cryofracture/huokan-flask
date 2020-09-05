from flask import Flask, render_template, flash, redirect, request
import uuid
from flask_bootstrap import Bootstrap
import psycopg2
from dotenv import load_dotenv
from datetime import datetime
import os
#from wtforms import Form, StringField, validators, SubmitField
#from wtforms.validators import InputRequired

load_dotenv()

app = Flask(__name__)
boostrap = Bootstrap(app)
app.config['SECRET_KEY'] = uuid.uuid1()

@app.route('/')
def main():
    #form = IDGenForm(request.form)
    # if request.method == 'POST' and form.validate():
    #     customerName = form.customerName.data
    #     advertiserName = form.advertiserName.data
    return render_template('main.html')

@app.route('/generated_id', methods = ['POST', 'GET'])
def generated():
    customer_uuid   = uuid.uuid1()
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")

    # print(customer_uuid)
    # print(customer_name)
    # print(advertiser_name)

    return render_template('generated.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name)

@app.route('/customercreationconfirmation', methods = ['POST'])
def confirmation():
    customer_uuid   = uuid.uuid1()
    customer_name   = request.form.get("customerName")
    advertiser_name = request.form.get("advertiserName")
    create_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    try:
        connection = psycopg2.connect(host = os.environ['DB_HOST'],
                                    port = os.environ['DB_PORT'],
                                    database = os.environ['DB_NAME'],
                                    user = os.environ['DB_USER'],
                                    password = os.environ['DB_PASS'])

        query = f""" INSERT INTO {os.environ['DB_SCHEMA']}.{os.environ['DB_TABLE']} ({os.environ['DB_COLS']}) VALUES ('{customer_uuid}','{customer_name}','{advertiser_name}','{create_date}') """

        connection = psycopg2.connect(user=os.environ['DB_USER'],
                                      password=os.environ['DB_PASS'],
                                      host=os.environ['DB_HOST'],
                                      port=os.environ['DB_PORT'],
                                      database=os.environ['DB_NAME'])
        cursor = connection.cursor()
        cursor.execute(query)
        connection.commit()
    #print(query)

    except psycopg2.Error as error:
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
        # print(existing_info[0])
        # print(existing_info[1])
        # print(existing_info[2])

        #flash('Customer already enrolled in rewards program. Please use existing ID.')

        return render_template('duplicate.html', existing_info=existing_info)#customer_name=customer_name, customer_id=customer_id, created_date=created_date)

    #print(existing_info)

    return render_template('confirmation.html', customer_name=customer_name, customer_uuid=customer_uuid, advertiser_name=advertiser_name, create_date=create_date)

# class IDGenForm(Form):
#     customerNameField = StringField('Customer Name', validators=[InputRequired])
#     advertiserNameField = StringField('Advertiser Name', validators=[validators.InputRequired])
#     submit = SubmitField('Get Customer ID')

if __name__ == '__main__':
    app.run()#debug=os.environ['FLASK_DEBUG_STATUS'], port=os.environ['FLASK_RUN_PORT'], host=os.environ['FLASK_RUN_HOST'])