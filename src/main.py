import datetime
import json
import os

from google.cloud.bigquery import Client
from google.oauth2.service_account import Credentials

from teamkatalogen import get_teams, get_po, link_naisteam_to_tk
from markedsplassen import get_dp, get_ds
from bq import df_to_table
from logger import create_logger
from config import TARGET_TABLE
from pandas_stuff import merge_sort_count, assign_unassigned


if __name__ == '__main__':

    _logger = create_logger(name="nada-data-analyse")

    credentials = Credentials.from_service_account_info(json.loads(os.environ["GOOGLE_SA_CREDS"]))
    client = Client(credentials=credentials, project=credentials.project_id)

    df_team = get_teams()
    df_po = get_po()

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

    df_merged = assign_unassigned(_logger, df_dp, df_ds, df_merged)

    df_merged["last_updated"] = datetime.datetime.utcnow().isoformat()

    try:
        err = df_to_table(client, df_merged, TARGET_TABLE)
        _logger.info(f"Successfully updated table {TARGET_TABLE}")
    except:
        _logger.error("Could not update dataset")
