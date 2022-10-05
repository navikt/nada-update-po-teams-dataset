from config import PROJECT_ID, DATASET, DATASTORY_TABLE, DATAPRODUCT_TABLE


def get_dp(client):
    query = f"""
        select REGEXP_EXTRACT(owner, '([^@]+)') naisteam, 'dataset' type, count(*) count
        from `{PROJECT_ID}.{DATASET}.{DATAPRODUCT_TABLE}`
        where version = (select max(version) from `{PROJECT_ID}.{DATASET}.{DATAPRODUCT_TABLE}`)
        group by REGEXP_EXTRACT(owner, '([^@]+)')
        """
    return client.query(query).result().to_dataframe()


def get_ds(client):
    query = f"""
        select owner naisteam, 'datastory' type, count(*) count 
        from `{PROJECT_ID}.{DATASET}.{DATASTORY_TABLE}` 
        group by owner
        """
    return client.query(query).result().to_dataframe()
