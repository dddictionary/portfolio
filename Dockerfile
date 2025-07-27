FROM python:3.9-slim-buster

# TODO: Change this workdir!!
WORKDIR .

COPY requirements.txt .

RUN pip3 install -r requirements.txt

COPY . .

CMD ["flask", "run", "--host=0.0.0.0"]

EXPOSE 5000
