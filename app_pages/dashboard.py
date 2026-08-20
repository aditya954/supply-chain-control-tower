"""Truck load utilization dashboard."""

from __future__ import annotations

import streamlit as st

from src.dock_vision.storage import (
    dashboard_metrics,
    load_inspections,
    metrics_by_route,
    metrics_by_warehouse,
    recent_inspections,
    sync_unsynced_to_snowflake,
)

st.header("Load utilization dashboard")
st.caption("Track truck fill rates, underloaded departures, and dock performance.")

toolbar = st.container(horizontal=True)
with toolbar:
    if st.button("Refresh data", width="content"):
        st.rerun()
    if st.button("Sync to Snowflake", width="content"):
        try:
            synced = sync_unsynced_to_snowflake()
            st.success(f"Synced {synced} inspection(s) to Snowflake.")
        except Exception as exc:  # noqa: BLE001
            st.error(f"Snowflake sync failed: {exc}")

frame = load_inspections()
metrics = dashboard_metrics(frame)

kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
kpi1.metric("Inspections", metrics["total_inspections"])
kpi2.metric("Avg load %", f"{metrics['avg_load_pct']:.1f}%")
kpi3.metric("Underloaded", metrics["underloaded_count"])
kpi4.metric("Optimal", metrics["optimal_count"])
kpi5.metric("Utilization gap", f"{metrics['utilization_gap']:.1f}%")

if frame.empty:
    st.info(
        "No inspections yet. Use the **Capture** page on a phone to photograph a truck "
        "and create the first record."
    )
else:
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.subheader("Average load by warehouse")
        warehouse_df = metrics_by_warehouse(frame)
        st.bar_chart(warehouse_df, x="warehouse_id", y="avg_load_pct")

    with chart_col2:
        st.subheader("Average load by route")
        route_df = metrics_by_route(frame)
        st.bar_chart(route_df, x="route_id", y="avg_load_pct")

    st.subheader("Status distribution")
    status_counts = frame["status"].value_counts().reset_index()
    status_counts.columns = ["status", "count"]
    st.bar_chart(status_counts, x="status", y="count")

    st.subheader("Recent inspections")
    st.dataframe(recent_inspections(frame), width="stretch", hide_index=True)

    with st.expander("Raw inspection data"):
        st.dataframe(frame, width="stretch", hide_index=True)
