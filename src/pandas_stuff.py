import pandas as pd


def merge_sort_count(df_dp, df_ds, df_tk):
    df_merged1 = df_tk.merge(df_dp, on="id_team", how="left")
    df_merged1["type"] = "dataset"
    df_merged2 = df_tk.merge(df_ds, on="id_team", how="left")
    df_merged2["type"] = "datastory"

    df_merged = pd.concat([df_merged1, df_merged2])

    df_merged = df_merged.sort_values(["name_po", "count"]).reset_index(drop=True)
    df_merged["count"] = df_merged["count"].fillna(0).astype(int)

    return df_merged


def assign_unassigned(_logger, df_dp, df_ds, df_merged):
    df_unassigned_dp = df_dp[df_dp["id_team"] == "unknown"]
    df_unassigned_ds = df_ds[df_ds["id_team"] == "unknown"]
    if df_unassigned_dp.shape[0] > 0:
        df_merged = pd.concat([df_merged, df_unassigned_dp]).fillna(
            value={"name_team": "unknown", "name_po": "unknown"})
        _logger.info(f"{df_unassigned_dp.shape[0]} naisteams with datasets are unassigned.")
    if df_unassigned_ds.shape[0] > 0:
        df_merged = pd.concat([df_merged, df_unassigned_ds]).fillna(
            value={"name_team": "unknown", "name_po": "unknown"})
        _logger.info(f"{df_unassigned_ds.shape[0]} naisteams with datastories are unassigned.")

    return df_merged
