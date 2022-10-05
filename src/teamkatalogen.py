import requests
import pandas as pd

from config import TEAMKATALOG_URL


def get_teams():
    r_team = requests.get(url=f'{TEAMKATALOG_URL}/team?status=ACTIVE')
    return pd.json_normalize(r_team.json()["content"])


def get_po():
    r_po = requests.get(url=f'{TEAMKATALOG_URL}/productarea?status=ACTIVE')
    return pd.json_normalize(r_po.json()["content"])


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


def link_naisteam_to_tk(naisteam, df_tk):
    i = 0
    while i < df_tk.shape[0]:
        if naisteam in df_tk.loc[i, "naisTeams"]:
            return df_tk.loc[i, "id_team"]
        elif naisteam in tk_link:
            return tk_link[naisteam]
        elif i == df_tk.shape[0] - 1:
            return "unknown"
        i += 1
