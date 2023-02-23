FROM python:3.12.0a5-bullseye
WORKDIR /NoccSchedulerApp
COPY requirements.txt requirements.txt

RUN pip3 install -r requirements.txt

COPY . .

CMD ['python3', 'manage.py', 'runserver', '0:8000']

#asdsadasda
