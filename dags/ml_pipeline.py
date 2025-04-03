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
    "ml_pipeline",
    description='End-to-end ML pipeline example',
    schedule_interval='0 0 1 * *',
    tags=['ml_pipeline'],
    default_args=default_args, 
    catchup=False) as dag:

    
    # task: 1
    fetching_data = PythonOperator(
        task_id='fetching_data',
        python_callable=load_data

    )
    
    # task: 2
    with TaskGroup('preparing_data') as preparing_data:

        # task: 3.1
        preprocessing = PythonOperator(
            task_id='preprocessing',
            python_callable=preprocess_data
        )

        # task: 3.2
        saving_batch_data = PythonOperator(
            task_id='saving_batch_data',
            python_callable=save_batch_data
        )
        
    # task: 4
    hyperparam_tuning = PythonOperator(
        task_id='hyperparam_tuning',
        python_callable=experiment
    )

    # task: 5
    with TaskGroup('after_crossvalidation') as after_crossvalidation:

        # =======
        # task: 5.1        
        saving_results = PythonOperator(
            task_id='saving_results',
            python_callable=track_experiments_info
        )

        # task: 5.2
        fitting_best_model = PythonOperator(
            task_id='fitting_best_model',
            python_callable=fit_best_model
        )    

    fetching_data >> preparing_data >> hyperparam_tuning >> after_crossvalidation