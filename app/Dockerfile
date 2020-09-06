FROM python:3.6

RUN pip install flask
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app


CMD [ "python", "app/application.py" ]