import streamlit as st
import pandas as pd
import plotly.express as px
from pathlib import Path

st.set_page_config(page_title="iPhone Sales Analysis", page_icon="📱", layout="wide")

DATA_PATH = Path(__file__).parent / "data" / "iphone_sales.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(DATA_PATH)
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    return df

st.title("📱 iPhone Sales Analysis & Visualization")
st.write("Interactive dashboard for exploring iPhone sales, revenue, models, and regions.")

try:
    df = load_data()
except Exception as e:
    st.error(f"Could not load the dataset: {e}")
    st.stop()

st.sidebar.header("Filters")
models = st.sidebar.multiselect("Select iPhone Model(s)", sorted(df["Model"].unique()), default=sorted(df["Model"].unique()))
regions = st.sidebar.multiselect("Select Region(s)", sorted(df["Region"].unique()), default=sorted(df["Region"].unique()))
filtered = df[df["Model"].isin(models) & df["Region"].isin(regions)].copy()

if filtered.empty:
    st.warning("No data matches the selected filters.")
    st.stop()

total_units = int(filtered["Units_Sold"].sum())
total_revenue = float(filtered["Revenue"].sum())
avg_price = float(filtered["Unit_Price"].mean())
top_model = filtered.groupby("Model")["Units_Sold"].sum().idxmax()

a, b, c, d = st.columns(4)
a.metric("Total Units Sold", f"{total_units:,}")
b.metric("Total Revenue", f"${total_revenue:,.0f}")
c.metric("Average Unit Price", f"${avg_price:,.0f}")
d.metric("Top Model", top_model)

c1, c2 = st.columns(2)
model_sales = filtered.groupby("Model", as_index=False)["Units_Sold"].sum()
fig1 = px.bar(model_sales.sort_values("Units_Sold", ascending=False), x="Model", y="Units_Sold", title="Units Sold by iPhone Model", text_auto=True)
c1.plotly_chart(fig1, use_container_width=True)

region_sales = filtered.groupby("Region", as_index=False)["Units_Sold"].sum()
fig2 = px.pie(region_sales, names="Region", values="Units_Sold", title="Units Sold by Region")
c2.plotly_chart(fig2, use_container_width=True)

model_revenue = filtered.groupby("Model", as_index=False)["Revenue"].sum()
fig3 = px.bar(model_revenue.sort_values("Revenue", ascending=False), x="Model", y="Revenue", title="Revenue by iPhone Model", text_auto=".2s")
st.plotly_chart(fig3, use_container_width=True)

monthly = filtered.set_index("Date").resample("MS")["Units_Sold"].sum().reset_index()
fig4 = px.line(monthly, x="Date", y="Units_Sold", markers=True, title="Monthly Units Sold")
st.plotly_chart(fig4, use_container_width=True)

st.subheader("Filtered Data")
st.dataframe(filtered.sort_values("Date", ascending=False), use_container_width=True)

st.download_button("⬇️ Download Filtered Data", filtered.to_csv(index=False).encode("utf-8"),
                   "filtered_iphone_sales.csv", "text/csv")
