FROM apache/airflow:2.3.0

COPY requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade pip \
    && pip install -r requirements.txt
 
