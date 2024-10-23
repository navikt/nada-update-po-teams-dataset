import datetime
import json
import logging
import os

from google.cloud.bigquery import Client
from google.oauth2.service_account import Credentials

from bq import df_to_table
from config import TARGET_TABLE
from markedsplassen import get_dp, get_ds
from pandas_stuff import assign_unassigned, merge_sort_count
from teamkatalogen import get_po, get_teams, link_naisteam_to_tk

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


if __name__ == '__main__':
    credentials = Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SA_CREDS"]))
    client = Client(credentials=credentials, project=credentials.project_id)

    logging.info("Getting teams from teamkatalogen")
    df_team = get_teams()
    logging.info(f"Got {df_team.shape[0]} teams")

    logging.info("Getting product areas from teamkatalogen")
    df_po = get_po()
    logging.info(f"Got {df_po.shape[0]} product areas")

    # merge team og po
    df_all = df_team.merge(df_po, left_on="productAreaId", right_on="id", suffixes=["_team", "_po"])
    df_tk = df_all.loc[:, ["id_team", "name_team", "name_po", "naisTeams"]]

    # hent datasett per naisteam
    df_dp = get_dp(client)
    df_ds = get_ds(client)

    # Kobler manuelt naisteams som ikke er registrert på et team i teamkatalogen.
    # naisteam: id_team (teamkatalog)
    df_dp["id_team"] = df_dp.naisteam.apply(lambda naisteam: link_naisteam_to_tk(naisteam, df_tk))
    df_ds["id_team"] = df_ds.naisteam.apply(lambda naisteam: link_naisteam_to_tk(naisteam, df_tk))

    df_merged = merge_sort_count(df_dp, df_ds, df_tk)

    df_merged = assign_unassigned(logging, df_dp, df_ds, df_merged)

    df_merged["last_updated"] = datetime.datetime.now(datetime.UTC).isoformat()

    logging.info(f"Trying to overwrite table {TARGET_TABLE} with {df_merged.shape[0]} rows")

    try:
        err = df_to_table(client, df_merged, TARGET_TABLE)
        logging.info(f"Successfully updated table {TARGET_TABLE}")
    except:
        logging.error("Could not update dataset")
