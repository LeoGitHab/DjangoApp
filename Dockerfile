FROM python:3.11
LABEL authors="leo"

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt requirements.txt

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

COPY mysite_19 .

CMD ["gunicorn", "mysite_19.wsgi:application", "--bind", "0.0.0.0:8000"]

#ENTRYPOINT ["top", "-b"]