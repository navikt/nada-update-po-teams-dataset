from config import PROJECT_ID, DATASET
from google.cloud.bigquery import LoadJobConfig


def df_to_table(client, df, target_table):
    table_id = f'{PROJECT_ID}.{DATASET}.{target_table}'
    job_config = LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )
    job = client.load_table_from_dataframe(df, table_id, job_config=job_config)

    return job.result()
