import datetime
import json
import os
import requests
import pandas as pd

from google.cloud.bigquery import Client, LoadJobConfig
from google.oauth2.service_account import Credentials

from config import PROJECT_ID, DATASET, DATAPRODUCT_TABLE, DATASTORY_TABLE, TARGET_TABLE, TEAMKATALOG_URL

if __name__ == '__main__':
    credentials = Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SA_CREDS"]))
    client = Client(credentials=credentials, project=credentials.project_id)

    r_team = requests.get(url=f'{TEAMKATALOG_URL}/team?status=ACTIVE')
    r_po = requests.get(url=f'{TEAMKATALOG_URL}/productarea?status=ACTIVE')
    df_team = pd.json_normalize(r_team.json()["content"])
    df_po = pd.json_normalize(r_po.json()["content"])

    # merge team og po
    df_all = df_team.merge(df_po, left_on="productAreaId", right_on="id", suffixes=["_team", "_po"])

    # hent datasett per naisteam
    df_dp = client.query(
        f"""
        select REGEXP_EXTRACT(owner, '([^@]+)') naisteam, 'dataset' type, count(*) count 
        from `{PROJECT_ID}.{DATASET}.{DATAPRODUCT_TABLE}` 
        where version = (select max(version) from `{PROJECT_ID}.{DATASET}.{DATAPRODUCT_TABLE}`) 
        group by REGEXP_EXTRACT(owner, '([^@]+)')
        """
    ).result().to_dataframe()
    df_ds = client.query(
        f"""select owner naisteam, 'datastory' type, count(*) count 
        from `{PROJECT_ID}.{DATASET}.{DATASTORY_TABLE}` 
        group by owner"""
    ).result().to_dataframe()

    df_tk = df_all.loc[:, ["id_team", "name_team", "name_po", "naisTeams"]]

    # Kobler manuelt naisteams som ikke er registrert på et team i teamkatalogen.
    # naisteam: id_team (teamkatalog)
    tk_link = {
        "arbeidsforhold": "29d44f3f-ff09-477c-b26a-83cd0aa66116",
        "yrkesskade": "270852c4-4c28-49a8-8189-a16897b31b95",
        "team-ai": "76f378c5-eb35-42db-9f4d-0e8197be0131",
        "spenn": "3c411c72-9587-4c6f-937e-2a404935b778",
        "nada": "5ade590e-3bc4-47fb-8b8d-552392f46376",
        "toi": "0150fd7c-df30-43ee-944e-b152d74c64d6",
        "teamia": "e6e3ce19-2cd3-491b-9ad9-817c2e9b7d96",
        "pensjon-saksbehandling": "45da0127-4d42-49b6-8130-e6c8e566abb8"
    }


    def link_naisteam_to_tk(naisteam):
        unassigned = True
        i = 0
        while i < df_tk.shape[0]:
            if naisteam in df_tk.loc[i, "naisTeams"]:
                return df_tk.loc[i, "id_team"]
            elif naisteam in tk_link:
                return tk_link[naisteam]
            elif i == df_tk.shape[0] - 1:
                return "unknown"
            i += 1

    df_dp["id_team"] = df_dp.naisteam.apply(lambda naisteam: link_naisteam_to_tk(naisteam))
    df_ds["id_team"] = df_ds.naisteam.apply(lambda naisteam: link_naisteam_to_tk(naisteam))

    df_merged1 = df_tk.merge(df_dp, on="id_team", how="left")
    df_merged1["type"] = "dataset"
    df_merged2 = df_tk.merge(df_ds, on="id_team", how="left")
    df_merged2["type"] = "datastory"

    df_merged = pd.concat([df_merged1, df_merged2])

    df_merged = df_merged.sort_values(["name_po", "count"]).reset_index(drop=True)
    df_merged["count"] = df_merged["count"].fillna(0).astype(int)

    df_unassigned_dp = df_dp[df_dp["id_team"] == "unknown"]
    df_unassigned_ds = df_ds[df_ds["id_team"] == "unknown"]
    if df_unassigned_dp.shape[0] > 0:
        df_merged = pd.concat([df_merged, df_unassigned_dp]).fillna(
            value={"name_team": "unknown", "name_po": "unknown"})
    if df_unassigned_ds.shape[0] > 0:
        df_merged = pd.concat([df_merged, df_unassigned_ds]).fillna(
            value={"name_team": "unknown", "name_po": "unknown"})

    df_merged["last_updated"] = datetime.datetime.utcnow().isoformat()

    table_id = f'{PROJECT_ID}.{DATASET}.{TARGET_TABLE}'

    job_config = LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",
    )

    job = client.load_table_from_dataframe(df_merged, table_id, job_config=job_config)

    error = job.result()