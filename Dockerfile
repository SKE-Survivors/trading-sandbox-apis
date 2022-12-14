FROM python:3.9-bullseye

RUN pip install --upgrade pip

WORKDIR /app

COPY . .
RUN pip install -r requirements.txt

EXPOSE 8080

CMD ["python", "src/app.py"]