FROM python:3.12-slim

WORKDIR /restaurant_management_backend

RUN apt-get update && apt-get install -y libpq-dev gcc

COPY requirements.txt /restaurant_management_backend/

RUN pip install --no-cache-dir -r requirements.txt

COPY . /restaurant_management_backend/

EXPOSE 8000

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
