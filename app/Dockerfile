FROM python:3.6

RUN pip install flask
COPY requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

#RUN set -o allexport; source .env; set +o allexport
EXPOSE 5000
EXPOSE 8080

CMD [ "python", "app/application.py" ]