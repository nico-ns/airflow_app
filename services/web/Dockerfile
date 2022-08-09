FROM python:3.9
 
WORKDIR /web
 
COPY ./requirements.txt /web/requirements.txt

COPY ./app /web/app/

RUN pip install --no-cache-dir --upgrade -r /web/requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
