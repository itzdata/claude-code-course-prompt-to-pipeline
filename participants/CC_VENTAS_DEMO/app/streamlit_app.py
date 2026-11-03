import streamlit as st
from snowflake.snowpark.context import get_active_session

st.set_page_config(page_title="Ventas Coffee", layout="wide")
session = get_active_session()
GOLD = "COFFEE_GOLD.CC_VENTAS_DEMO"  # el dashboard lee solo de Gold


@st.cache_data(ttl=600)
def load(sql: str):
    return session.sql(sql).to_pandas()


st.title("Ventas por tienda y producto")

stores = load(f"SELECT DISTINCT STORE_NAME FROM {GOLD}.AGG_SALES_DAILY_STORE ORDER BY 1")["STORE_NAME"].tolist()
chosen = st.sidebar.multiselect("Tienda", stores, default=stores)
if not chosen:
    st.warning("Selecciona al menos una tienda.")
    st.stop()
in_list = ",".join("'" + s.replace("'", "''") + "'" for s in chosen)
where = f"WHERE STORE_NAME IN ({in_list})"

kpi = load(f"SELECT SUM(TOTAL_AMT) AS V, SUM(ORDER_CNT) AS O, SUM(TOTAL_AMT)/NULLIF(SUM(ORDER_CNT),0) AS T "
           f"FROM {GOLD}.AGG_SALES_DAILY_STORE {where}").iloc[0]
c1, c2, c3 = st.columns(3)
c1.metric("Ventas (USD)", f"{kpi['V']:,.0f}")
c2.metric("Órdenes", f"{kpi['O']:,.0f}")
c3.metric("Ticket promedio (USD)", f"{kpi['T']:,.2f}")

left, right = st.columns(2)
with left:
    st.subheader("Ventas por mes")
    m = load(f"SELECT DATE_TRUNC(MONTH, ORDER_DATE) AS MES, SUM(TOTAL_AMT) AS VENTAS "
             f"FROM {GOLD}.AGG_SALES_DAILY_STORE {where} GROUP BY 1 ORDER BY 1")
    st.line_chart(m, x="MES", y="VENTAS")
with right:
    st.subheader("Ventas por categoría")
    c = load(f"SELECT CATEGORY_NAME, SUM(TOTAL_AMT) AS VENTAS FROM {GOLD}.AGG_SALES_DAILY_STORE {where} GROUP BY 1 ORDER BY 2 DESC")
    st.bar_chart(c, x="CATEGORY_NAME", y="VENTAS")

st.subheader("Ranking de tiendas")
r = load(f"SELECT STORE_NAME, CITY_NAME, SUM(TOTAL_AMT) AS VENTAS, SUM(ORDER_CNT) AS ORDENES "
         f"FROM {GOLD}.AGG_SALES_DAILY_STORE {where} GROUP BY 1, 2 ORDER BY 3 DESC")
st.dataframe(r, use_container_width=True, hide_index=True)
