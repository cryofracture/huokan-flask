[![Build Status](https://travis-ci.org/cryofracture/huokan-flask.svg?branch=master)](https://travis-ci.org/cryofracture/huokan-flask)

# Huokan-Flask

A containerized flask application with nginx reverse proxy and a postgres database for Customer ID Generation.

# Flask
A bootstraped site for Huokan Advertisers to enter customers into Rewards Membership Program. If customer already exists, the database will return the customer's ID.

# Nginx
A reverse proxy web server for Flask.

# Postgres
It's quick, easy, and powerful.

# Docker 
Docker-compose compiles standard postgres and nginx images with ports exposed/forwarded as needed, as well as a custom python docker image with the Huokan ID generator code installed.