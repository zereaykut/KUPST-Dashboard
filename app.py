import warnings
from datetime import date, timedelta

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import requests
import streamlit as st
from plotly.subplots import make_subplots

warnings.filterwarnings("ignore")

# INFO: https://editor.swagger.io/?url=https://seffaflik.epias.com.tr/electricity-service/technical/tr/swagger.json

st.set_page_config(page_title="KUPST Dashboard", layout="wide")

main_url = "https://seffaflik.epias.com.tr/electricity-service"


def control_date(start_date: date, end_date: date):
    delta = end_date - start_date
    if start_date > end_date:
        return "Start Date can't be greater than end date"
    elif delta.days >= 30:
        return f"Date range can't be greater than 30 days. Used date range is {delta.days} days."
    else:
        return 200


def get_org_info(start_date: date, end_date: date):
    response = requests.post(
        f"{main_url}/v1/generation/data/organization-list",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "endDate": f"{end_date}T23:00:00+03:00",
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
    else:
        data = "response error"
    return data


def get_uevcb_info(start_date: date, org_id: int):
    response = requests.post(
        f"{main_url}/v1/generation/data/uevcb-list",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "organizationId": org_id,
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
    else:
        data = "response error"
    return data


def get_grt_info():
    response = requests.get(f"{main_url}/v1/generation/data/powerplant-list")
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
    else:
        data = "response error"
    return data


def get_kudup(uevcb_id: int, org_id: int, start_date: date, end_date: date):
    response = requests.post(
        f"{main_url}/v1/generation/data/sbfgp",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "endDate": f"{end_date}T23:00:00+03:00",
            "organizationId": org_id,
            "uevcbId": uevcb_id,
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
            data["date"] = pd.to_datetime(data["date"].str.split("+", expand=True)[0])
            data = data[["date", "toplam"]].rename(columns={"toplam": "kudup"})
    else:
        data = "response error"
    return data


def get_grt(grt_id: int, start_date: date, end_date: date):
    response = requests.post(
        f"{main_url}/v1/generation/data/realtime-generation",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "endDate": f"{end_date}T23:00:00+03:00",
            "powerPlantId": grt_id,
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
            data["date"] = pd.to_datetime(data["date"].str.split("+", expand=True)[0])
            data = data[["date", "total"]].rename(columns={"total": "grt"})
    else:
        data = "response error"
    return data


def get_mcp(start_date: date, end_date: date):
    response = requests.post(
        f"{main_url}/v1/markets/dam/data/mcp",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "endDate": f"{end_date}T23:00:00+03:00",
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
            data["date"] = pd.to_datetime(data["date"].str.split("+", expand=True)[0])
            data = data[["date", "price"]].rename(columns={"price": "mcp"})
    else:
        data = "response error"
    return data


def get_smp(start_date: date, end_date: date):
    response = requests.post(
        f"{main_url}/v1/markets/bpm/data/system-marginal-price",
        json={
            "startDate": f"{start_date}T00:00:00+03:00",
            "endDate": f"{end_date}T23:00:00+03:00",
            "region": "TR1",
        },
    )
    if response.status_code == 200:
        data = response.json()
        data = data.get("items", None)
        if data is None:
            data = "response is None or Empty"
        else:
            data = pd.DataFrame(data)
            data["date"] = pd.to_datetime(data["date"].str.split("+", expand=True)[0])
            data = data[["date", "systemMarginalPrice"]].rename(
                columns={"systemMarginalPrice": "smp"}
            )
    else:
        data = "response error"
    return data


def kupst(df, tolerance_coefficient: int):
    df["tolerance_coefficient"] = tolerance_coefficient

    df["imbalance_amount"] = df["grt"] - df["kudup"]
    # Tolerance Amount
    df["tolerance_amount"] = df["kudup"] * df["tolerance_coefficient"]
    # Tolerance Exceed Imbalance Amount
    df["tolerance_exceed_imbalance_amount"] = df[
        (abs(df["imbalance_amount"]) > df["tolerance_amount"])
    ]["imbalance_amount"]

    # Positive Imbalance Amount
    df["positive_imbalance_amount"] = df[df["imbalance_amount"] >= 0][
        "imbalance_amount"
    ]
    df["negative_imbalance_amount"] = df[df["imbalance_amount"] < 0]["imbalance_amount"]

    # Positive Imbalance Payment
    df["positive_imbalance_payment"] = (
        df["positive_imbalance_amount"] * df[["mcp", "smp"]].min(axis=1) * 0.97
    )
    df["negative_imbalance_payment"] = (
        df["negative_imbalance_amount"] * df[["mcp", "smp"]].max(axis=1) * 1.03
    )
    # Imbalance Payment
    df["imbalance_payment"] = df[
        ["positive_imbalance_payment", "negative_imbalance_payment"]
    ].sum(axis=1)

    # Imbalance Cost
    df["imbalance_cost"] = df["imbalance_amount"] * df["mcp"] - df["imbalance_payment"]
    # .unit Imbalance Cost
    df["unit_imbalance_cost"] = df["imbalance_cost"] / df["grt"].replace(0, np.nan)

    ## KUPST
    df["mcp_smp_3_percent"] = df[["mcp", "smp"]].max(axis=1) * 0.03

    df["kupsm"] = abs(df["tolerance_exceed_imbalance_amount"]) - df["tolerance_amount"]
    df["kupst"] = df["kupsm"] * df["mcp_smp_3_percent"]

    df["unit_kupst"] = df["kupst"] / df["grt"].replace(0, np.nan)
    return df


def kupst_report(df):
    tolerance_coefficient = df["tolerance_coefficient"].mean()
    total_generation = df["grt"].sum()
    total_imbalance_payment = df["imbalance_payment"].sum()
    total_positive_eia = df["positive_imbalance_amount"].sum()
    total_negative_eia = df["negative_imbalance_amount"].sum()
    total_imbalance_cost = df["imbalance_cost"].sum()
    unit_imbalance_cost = total_imbalance_cost / total_generation
    unit_kupst_cost = df["kupst"].sum() / total_generation
    total_kupst_cost = df["kupst"].sum()
    imbalance_plus_kupst_unit_cost = unit_imbalance_cost + unit_kupst_cost

    dict_report = {
        "Total Generation": [total_generation],
        "Total Electricity Imbalance Payment": [total_imbalance_payment],
        "Total Imbalance Cost": [total_imbalance_cost],
        "Unit Imbalance Cost": [unit_imbalance_cost],
        "Unit KUPST Cost": [unit_kupst_cost],
        "Total KUPST Cost": [total_kupst_cost],
        "Imbalance + Unit KUPST Cost": [imbalance_plus_kupst_unit_cost],
        "Total Positive Electricity Imbalance Amount": [total_positive_eia],
        "Total Negative Electricity Imbalance Amount": [total_negative_eia],
    }
    df_report = pd.DataFrame(dict_report)
    return df_report


def convert_df(df):
    return df.to_csv().encode("utf-8")


def main():
    tab1, tab2, tab3 = st.tabs(["KUPST", "About Dashboard", "Contact"])

    with tab1:
        st.subheader("Parameters")
        # Parameters
        col1, col2, col3 = st.columns(3)
        start_date = col1.date_input(
            "Start Day", value=date.today() - timedelta(days=7)
        )
        end_date = col2.date_input("End Day", value=date.today() - timedelta(days=1))

        error = control_date(start_date, end_date)

        if error == 200:
            # Get Info
            col1, col2, col3 = st.columns(3)
            df_org_info = get_org_info(start_date, end_date)
            org_name = col1.selectbox(
                "Select Organization for KUDÜP Data",
                df_org_info["organizationName"],
                index=int(
                    df_org_info[
                        df_org_info["organizationName"]
                        == "SİBELRES ELEKTRİK ÜRETİM A.Ş."
                    ].reset_index()["index"]
                ),
            )
            org_info = df_org_info[df_org_info["organizationName"] == org_name]
            org_id = int(org_info["organizationId"])

            df_uevcb_info = get_uevcb_info(start_date, org_id)
            uevcb_name = col2.selectbox(
                "Select Powerplant for KUDÜP Data", df_uevcb_info["name"], index=0
            )
            uevcb_info = df_uevcb_info[df_uevcb_info["name"] == uevcb_name]
            uevcb_id = int(uevcb_info["id"])

            df_grt_info = get_grt_info()
            grt_name = col3.selectbox(
                "Select Powerplant for Real Time Generation Data",
                df_grt_info["name"],
                index=int(
                    df_grt_info[
                        df_grt_info["name"] == "SİBEL RES-40W0000000156631"
                    ].reset_index()["index"]
                ),
            )
            grt_info = df_grt_info[df_grt_info["name"] == grt_name]
            grt_id = int(grt_info["id"])

            tolerance_coefficient = col1.number_input(
                "Choose tolerance coefficient", min_value=0.05, max_value=0.9, value=0.1
            )

            # Get Data
            df_grt = get_grt(grt_id, start_date, end_date)
            df_kudup = get_kudup(uevcb_id, org_id, start_date, end_date)
            df_mcp = get_mcp(start_date, end_date)
            df_smp = get_smp(start_date, end_date)

            df = pd.concat(
                [
                    df_grt.set_index("date"),
                    df_kudup.set_index("date"),
                    df_mcp.set_index("date"),
                    df_smp.set_index("date"),
                ],
                axis=1,
            )

            df = kupst(df, tolerance_coefficient)
            df_report = kupst_report(df)

            st.subheader("Graphs")

            fig = go.Figure()
            fig.add_trace(
                go.Scatter(
                    x=df.index, y=df["grt"], mode="lines", name="Real Time Generation"
                )
            )
            fig.add_trace(
                go.Scatter(x=df.index, y=df["kudup"], mode="lines", name="KUDÜP")
            )
            fig.update_layout(title_text="Real Time Generation & KUDÜP", hovermode="x unified")
            st.plotly_chart(fig, theme="streamlit", use_container_width=True)

            fig_imbalance_amount = go.Figure()
            fig_imbalance_amount.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["positive_imbalance_amount"].fillna(0),
                    mode="lines",
                    name="Positive Imbalance",
                    marker={"color": "red"},
                )
            )
            fig_imbalance_amount.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["negative_imbalance_amount"].fillna(0),
                    mode="lines",
                    name="Negative Imbalance",
                    marker={"color": "blue"},
                )
            )
            fig_imbalance_amount.update_layout(title_text="Imbalance Amount", hovermode="x unified")
            st.plotly_chart(
                fig_imbalance_amount, theme="streamlit", use_container_width=True
            )

            fig_imbalance_cost = make_subplots(specs=[[{"secondary_y": True}]])
            fig_imbalance_cost.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["imbalance_cost"].fillna(0),
                    mode="lines",
                    name="Imbalance Cost",
                    marker={"color": "red"},
                ),
                secondary_y=True,
            )
            fig_imbalance_cost.add_trace(
                go.Scatter(
                    x=df.index,
                    y=df["kupst"].fillna(0),
                    mode="lines",
                    name="Kupst",
                    marker={"color": "blue"},
                ),
                secondary_y=False,
            )
            # fig_imbalance_cost.add_trace(go.Scatter(x=df.index, y=df["kupsm"].fillna(0), mode="lines", name="Kupsm", marker={"color":"black"}), secondary_y=True)
            fig_imbalance_cost.update_layout(title_text="Kupst", hovermode="x unified")
            fig_imbalance_cost.update_yaxes(
                title_text="Imbalance Cost", secondary_y=True
            )
            fig_imbalance_cost.update_yaxes(title_text="Kupst", secondary_y=False)
            st.plotly_chart(
                fig_imbalance_cost, theme="streamlit", use_container_width=True
            )
            st.subheader("Summary")
            st.dataframe(df_report.round(2), hide_index=True,)

            col1, col2, col3, col4 = st.columns(4)

            csv = convert_df(df_report.round(2))
            col1.download_button(
                "Download summary data as csv",
                csv,
                f"{grt_name}-{start_date}-{end_date}.csv",
                "text/csv",
            )

            csv = convert_df(df)
            col2.download_button(
                "Download main data as csv",
                csv,
                f"{grt_name}-{start_date}-{end_date}.csv",
                "text/csv",
            )

        else:
            st.error(error)

    with tab2:
        st.header("KUPST Dashboard")
        st.write("This Dashboard calculates the imbalance that occurs from a powerpalnt's deviation from its planned generation with use of EPİAŞ Transparency API")
        st.subheader("Note")
        st.write(
            "KUDÜP and Real Time Generation data selection sections operate separately. It is not checked in the background whether the switchboards of these two data are matched. For this reason, the user is responsible for ensuring that the parameters selected for KUDÜP and Real Time Production Data match."
        )
        st.subheader("Data")
        st.write("""**MCP:** Market Clearing Price [TL/MWh]""")
        st.write("""**SMP:** System Marginal Price [TL/MWh]""")
        st.write("""**Real Time Generation (GRT):** Hourly generation of selected powerplant [MWh]""")
        st.write("""**KUDÜP:** Hourly Finalized Settlement Period Production Plan of selected powerplant [MWh]""")
        st.subheader("Calculation")
        st.image("assets/KUPST_Imbalance_Cost.png", caption="Imbalance Cost")
        st.image("assets/KUPST_Kupst.png", caption="KÜPST")
        st.image("assets/KUPST_Unit_Cost.png", caption="Unit Cost")
        st.subheader("Source")
        st.page_link("https://seffaflik.epias.com.tr/home", label="EPİAŞ")
        st.page_link("https://seffaflik.epias.com.tr/electricity-service/technical/tr/index.html", label="Trancparency API")

    with tab3:
        st.page_link("https://github.com/zereaykut", label="Github")
        st.page_link("https://www.linkedin.com/in/halil-aykut-zere-90694520b/", label="LinkedIn")


if __name__ == "__main__":
    main()
