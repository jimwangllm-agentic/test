"""Interactive example analytics dashboard built with Streamlit."""

from datetime import date

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st


st.set_page_config(page_title="Pulse Dashboard", page_icon="📊", layout="wide")

REGIONS = {
    "West": (37.7749, -122.4194),
    "Central": (41.8781, -87.6298),
    "South": (32.7767, -96.7970),
    "East": (40.7128, -74.0060),
    "Southeast": (33.7490, -84.3880),
}
PRODUCTS = ["Analytics", "Automation", "Collaboration", "Security"]
PRODUCT_COLORS = {
    "Analytics": "#4F46E5",
    "Automation": "#0EA5E9",
    "Collaboration": "#14B8A6",
    "Security": "#F59E0B",
}


@st.cache_data
def make_example_data() -> pd.DataFrame:
    """Create a deterministic, realistic-looking sales dataset."""
    rng = np.random.default_rng(42)
    dates = pd.date_range("2025-01-01", "2025-12-31", freq="D")
    rows = []
    for day in dates:
        seasonal = 1 + 0.22 * np.sin((day.dayofyear - 45) * 2 * np.pi / 365)
        for region, (lat, lon) in REGIONS.items():
            for product in PRODUCTS:
                orders = rng.poisson(5 * seasonal)
                unit_value = {"Analytics": 210, "Automation": 155, "Collaboration": 120, "Security": 180}[product]
                revenue = max(0, orders * unit_value * rng.normal(1, 0.16))
                rows.append(
                    {
                        "date": day,
                        "region": region,
                        "product": product,
                        "orders": orders,
                        "revenue": revenue,
                        "latitude": lat + rng.normal(0, 0.32),
                        "longitude": lon + rng.normal(0, 0.32),
                    }
                )
    return pd.DataFrame(rows)


data = make_example_data()
st.title("Pulse Dashboard")
st.caption("Example revenue and customer activity for 2025")

with st.sidebar:
    st.header("Filters")
    date_range = st.date_input(
        "Date range",
        value=(date(2025, 1, 1), date(2025, 12, 31)),
        min_value=data["date"].min().date(),
        max_value=data["date"].max().date(),
    )
    selected_regions = st.multiselect("Regions", list(REGIONS), default=list(REGIONS))
    st.caption("All figures use generated example data.")

if len(date_range) != 2 or not selected_regions:
    st.info("Select a complete date range and at least one region to see the dashboard.")
    st.stop()

start_date, end_date = map(pd.Timestamp, date_range)
filtered = data[
    data["date"].between(start_date, end_date) & data["region"].isin(selected_regions)
].copy()

revenue = filtered["revenue"].sum()
orders = int(filtered["orders"].sum())
average_order = revenue / orders if orders else 0
prior_period = data[
    data["date"].between(start_date - (end_date - start_date + pd.Timedelta(days=1)), start_date - pd.Timedelta(days=1))
    & data["region"].isin(selected_regions)
]["revenue"].sum()
revenue_delta = (revenue / prior_period - 1) if prior_period else None

metric_1, metric_2, metric_3 = st.columns(3)
metric_1.metric("Revenue", f"${revenue:,.0f}", f"{revenue_delta:+.1%}" if revenue_delta is not None else "—")
metric_2.metric("Orders", f"{orders:,}")
metric_3.metric("Average order value", f"${average_order:,.0f}")

left, right = st.columns(2)
with left:
    st.subheader("Revenue over time")
    monthly = filtered.groupby(pd.Grouper(key="date", freq="MS"), as_index=False)["revenue"].sum()
    trend = px.line(monthly, x="date", y="revenue", markers=True, labels={"date": "Month", "revenue": "Revenue ($)"})
    trend.update_traces(line_color="#4F46E5")
    trend.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=330)
    st.plotly_chart(trend, use_container_width=True)

with right:
    st.subheader("Revenue by region")
    by_region = filtered.groupby("region", as_index=False)["revenue"].sum().sort_values("revenue")
    bars = px.bar(by_region, x="revenue", y="region", orientation="h", labels={"revenue": "Revenue ($)", "region": ""}, color_discrete_sequence=["#0EA5E9"])
    bars.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=330, showlegend=False)
    st.plotly_chart(bars, use_container_width=True)

left, right = st.columns(2)
with left:
    st.subheader("Product mix")
    by_product = filtered.groupby("product", as_index=False)["revenue"].sum()
    pie = px.pie(by_product, values="revenue", names="product", color="product", color_discrete_map=PRODUCT_COLORS, hole=0.45)
    pie.update_traces(textinfo="percent+label")
    pie.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=360, legend_title_text="")
    st.plotly_chart(pie, use_container_width=True)

with right:
    st.subheader("Revenue heatmap")
    heatmap_data = filtered.pivot_table(index="region", columns="product", values="revenue", aggfunc="sum", fill_value=0).reindex(index=selected_regions, columns=PRODUCTS, fill_value=0)
    heatmap = go.Figure(
        go.Heatmap(
            z=heatmap_data.values,
            x=heatmap_data.columns,
            y=heatmap_data.index,
            colorscale="Blues",
            hovertemplate="Region: %{y}<br>Product: %{x}<br>Revenue: $%{z:,.0f}<extra></extra>",
        )
    )
    heatmap.update_layout(margin=dict(l=0, r=0, t=10, b=0), height=360, xaxis_title="Product", yaxis_title="Region")
    st.plotly_chart(heatmap, use_container_width=True)

st.subheader("Customer activity map")
map_points = (
    filtered.groupby("region", as_index=False)
    .agg(latitude=("latitude", "mean"), longitude=("longitude", "mean"), revenue=("revenue", "sum"), orders=("orders", "sum"))
)
activity_map = px.scatter_map(
    map_points,
    lat="latitude",
    lon="longitude",
    size="revenue",
    color="orders",
    hover_name="region",
    hover_data={"revenue": ":$,.0f", "orders": ":,"},
    color_continuous_scale="Viridis",
    size_max=42,
    zoom=3,
    center={"lat": 39.5, "lon": -98.35},
    map_style="open-street-map",
)
activity_map.update_layout(margin=dict(l=0, r=0, t=0, b=0), height=480)
st.plotly_chart(activity_map, use_container_width=True)
