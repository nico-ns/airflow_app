from datetime import datetime, timedelta
from airflow.decorators import dag, task
from sqlalchemy import create_engine, insert
import os
import csv
from utilities.models import metadata_obj, Users, Events

# SET PATHS AND CONFIGURATIONS
default_args = {
	"owner": "me",
	"retries": 5, 
	"retry_delay": timedelta(minutes=2)
}

STORAGE_PATH = "/usr/src/data/"
LOG_PATH = "opt/airflow/logs"


# DEFINE DAG AND TASKS
@dag(
	dag_id="dag_startup_v1",
	default_args=default_args,
	description="Connecting to DB and creating tables",
	start_date=datetime(2022, 6, 24, 2),
	schedule_interval="@once",
	catchup=False
	)
def startup():


	@task(task_id="db_connect_and_create")
	def create_tables():

		db2 = create_engine(os.environ["AIRFLOW_DB_CONN"])
		print("Creating tables in DB")
		metadata_obj.create_all(db2)


	@task(task_id="load_users_csv")
	def load_csv():
		file_path = STORAGE_PATH + "users/users.csv"
		# if "users.csv" in os.listdir(file_path):
		try:
			with open(file_path + "users.csv", "r") as source:
				reader = csv.DictReader(source)
				fields = reader.fieldnames
				return list(reader)
		except FileNotFoundError:
			print("users.csv was not in the specified path")
			return []


	@task(task_id="load_users_db")
	def load_users(users):

		if users:

			db = create_engine(os.environ["AIRFLOW_DB_CONN"])
			with db.begin() as transaction:
				print("Inserting users in DB")
				print(type(users))
				print(users)
				result = transaction.execute(insert(Users), [{
					"user_id": r["id"],
					"storage": float(r["storage"]) / (10 ** 9),
					"created": r["created"]
					} for r in users])

				return result

		else:
			print("No users to insert!")
			return

	tables = create_tables()
	users = load_csv()
	load = load_users(users)

	tables >> load



dag_instance = startup()
