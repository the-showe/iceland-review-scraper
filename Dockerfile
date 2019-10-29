FROM python:3.6
RUN pip install pipenv
COPY . /app
WORKDIR /app
RUN pipenv install --deploy --ignore-pipfile
CMD ["pipenv", "run", "python", "app.py"]
