from airflow.models import DAG

from airflow.operators.python import PythonOperator
from airflow.providers.postgres.operators.postgres import PostgresOperator
from airflow.utils.task_group import TaskGroup

from datetime import datetime

from utils.load_data import load_data
from utils.preprocess_data import preprocess_data
from utils.experiment import experiment
from utils.track_experiments_info import track_experiments_info
from utils.fit_best_model import fit_best_model
from utils.save_batch_data import save_batch_data


default_args= {
    'owner': 'Nitin Swarnkar',
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': 5,
    'start_date': datetime(2021, 12, 1)
}

# Create a DAG object with schedule to run on First of the month at midnight
with DAG(
    "table_creation",
    description='End-to-end ML pipeline example',
    schedule_interval='0 0 1 * *',
    tags=['initialization'],
    default_args=default_args, 
    catchup=False) as dag:
        creating_experiment_tracking_table = PostgresOperator(
            task_id="creating_experiment_tracking_table",
            postgres_conn_id='postgres_default',
            sql='sql/create_experiments.sql'
        )
        creating_food_prices_table = PostgresOperator(
            task_id="creating_food_prices_table",
            postgres_conn_id='postgres_default',
            sql='sql/create_food_prices_table.sql'
        )

        creating_experiment_tracking_table >> creating_food_prices_table