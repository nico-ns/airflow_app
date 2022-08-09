from airflow.decorators import dag, task
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python import get_current_context
from airflow.models import XCom
from airflow.utils.session import provide_session

from utilities.models import Events
from utilities.customsensor import CustomFileSensor

from sqlalchemy import create_engine, insert

from datetime import datetime, timedelta
import os
import json


# SET PATHS AND CONFIGURATIONS
default_args = {
    "owner": "me",
    "retries": 5, 
    "retry_delay": timedelta(minutes=2)
}

STORAGE_PATH = "/usr/src/data/"
DB_CONN_STRING = os.environ["AIRFLOW_DB_CONN"]


# DEFINE DAG AND TASKS
@dag(
    dag_id="dag_events_v1",
    default_args=default_args,
    description="Events ETL pipeline",
    start_date=datetime(2022, 6, 24, 2),
    schedule_interval="@once",
    catchup=False
    )
def etl_events():

    @task(task_id="extraction")
    def extract_events():
        context = get_current_context()
        ti = context["ti"]
        files = ti.xcom_pull(task_ids="file_sensor", key="files")
        # print(files)

        extracted = []
        for file in files:
            with open(file, "r") as f:
                file_content = json.load(f)
                extracted += list(file_content.values())

        return extracted

    @task(task_id="cleansing")
    def clean_events(events):
        cleaned_events =  [{
          "user_id": event["client.user_id"],
          "direction": event["direction"],
          "size" : event["size"],
          "status" : event["status"],
          "timestamp" : event["timestamp"],
          "transfer_time" : event["time.backend"],
          "transfer_speed" : float(event["size"]) / float(event["time.backend"])} for event in events]

        return cleaned_events

    @task(task_id="loading")
    def load_events(ev):
        db = create_engine(DB_CONN_STRING)
        with db.begin() as transaction:
            transaction.execute(insert(Events), ev)

    @task(task_id="remove_file")
    def remove_file():
        context = get_current_context()
        ti = context["ti"]
        files = ti.xcom_pull(task_ids="file_sensor", key="files")
        if files:
            for file in files:
                os.remove(file)

    @task(task_id="clean_xcom")
    @provide_session
    def delete_xcom(key: str, task_id: str, dag_id: str, session=None) -> None:
        session.query(XCom).filter(XCom.key==key, XCom.task_id==task_id, XCom.dag_id==dag_id).delete()
        session.commit()
        

    sensing_task = CustomFileSensor(filepath=STORAGE_PATH, 
      fs_conn_id="file_sensing",
      task_id="file_sensor",
      poke_interval=20,
      file_type="json")

    events = extract_events()
    cleaned_events = clean_events(events)
    loaded = load_events(cleaned_events)

    rem = remove_file()
    xcom_del = delete_xcom(key="files", task_id="file_sensor", dag_id="dag_events_v1")

    sensing_task >> events >> rem
    loaded >> xcom_del


dag_instance = etl_events()
