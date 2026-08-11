FROM python:3.11.15-slim-trixie AS build

WORKDIR /app

COPY requirements.txt .

RUN pip install --upgrade pip

RUN pip install --no-cache-dir -r requirements.txt

FROM python:3.11.15-slim-trixie

WORKDIR /app

COPY --from=build /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=build /usr/local/bin /usr/local/bin

COPY . .

EXPOSE 8080

CMD ["python3", "manage.py", "runserver", "0.0.0.0:8080"]
