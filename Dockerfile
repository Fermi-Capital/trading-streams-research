FROM ubuntu:16.04

RUN apt-get update -y && \
    apt-get install -y python-pip python-dev

# We copy just the requirements.txt first to leverage Docker cache
COPY ./reqs.txt /app/requirements.txt

WORKDIR /app

RUN pip install -r reqs.txt

COPY . /app

ENTRYPOINT [ "python" ]

CMD [ "server.py" ]

#docker build -t flask-tutorial:latest .

#docker run -d -p 5000:5000 flask-tutorial