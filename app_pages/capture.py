"""Mobile-friendly truck photo capture for load inspection."""

from __future__ import annotations

import streamlit as st

from src.dock_vision.analyzer import TARGET_LOAD_PCT, analyze_truck_load
from src.dock_vision.schemas import LoadInspection, LoadStatus
from src.dock_vision.storage import append_inspection, save_photo, sync_unsynced_to_snowflake

STATUS_COLORS = {
    LoadStatus.OPTIMAL.value: "#16a34a",
    LoadStatus.UNDERLOADED.value: "#ea580c",
    LoadStatus.OVERLOADED.value: "#dc2626",
    LoadStatus.UNSAFE.value: "#b91c1c",
}


st.header("Dock capture")
st.caption("Take a rear-door photo to estimate truck load completion.")

with st.form("capture_form", clear_on_submit=False):
    truck_id = st.text_input("Truck ID", placeholder="TRK-4472")
    trip_id = st.text_input("Trip ID", placeholder="TRIP-10021")
    col1, col2 = st.columns(2)
    with col1:
        warehouse_id = st.selectbox("Warehouse", ["LON", "MAN", "BHM", "GLA"])
    with col2:
        dock_id = st.selectbox("Dock", ["D01", "D02", "D03", "D04"])
    route_id = st.text_input("Route ID", placeholder="RT-MAN-01")
    col3, col4 = st.columns(2)
    with col3:
        planned_pallets = st.number_input("Planned pallets", min_value=1, max_value=40, value=24)
    with col4:
        planned_load_pct = st.number_input(
            "Planned load %",
            min_value=50.0,
            max_value=100.0,
            value=100.0,
            step=1.0,
        )

    photo = st.camera_input("Truck rear photo", label_visibility="collapsed")
    submitted = st.form_submit_button("Analyze load", type="primary", width="stretch")

if submitted:
    if not photo:
        st.error("Please capture or upload a truck photo first.")
    elif not truck_id.strip() or not trip_id.strip() or not route_id.strip():
        st.error("Truck ID, Trip ID, and Route ID are required.")
    else:
        image_bytes = photo.getvalue()
        with st.spinner("Analyzing truck load..."):
            analysis = analyze_truck_load(
                image_bytes,
                planned_load_pct=planned_load_pct,
                target_load_pct=TARGET_LOAD_PCT,
            )
            inspection = LoadInspection.create(
                truck_id=truck_id,
                trip_id=trip_id,
                warehouse_id=warehouse_id,
                route_id=route_id,
                dock_id=dock_id,
                planned_pallets=int(planned_pallets),
                planned_load_pct=float(planned_load_pct),
                analysis=analysis,
            )
            photo_path = save_photo(inspection.inspection_id, image_bytes)
            inspection.photo_path = photo_path
            record = append_inspection(inspection)

        color = STATUS_COLORS.get(analysis.status.value, "#334155")
        st.markdown(
            f"""
            <div style="padding: 1rem; border-radius: 12px; background: {color}15;
            border: 1px solid {color}; margin-bottom: 1rem;">
            <h3 style="margin:0; color:{color};">{analysis.status.value}</h3>
            <p style="margin:0.5rem 0 0 0;">Estimated load: <b>{analysis.estimated_load_pct:.1f}%</b>
            (target {TARGET_LOAD_PCT:.0f}%)</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(3)
        metric_cols[0].metric("Confidence", f"{analysis.confidence * 100:.0f}%")
        metric_cols[1].metric("Cargo fill score", f"{analysis.cargo_fill_score:.2f}")
        metric_cols[2].metric("Uneven load score", f"{analysis.uneven_load_score:.2f}")

        if analysis.issue_codes:
            st.warning("Issues: " + ", ".join(analysis.issue_codes))
        st.info(analysis.recommendation)

        action = st.segmented_control(
            "Supervisor action",
            options=["HOLD", "TOP_UP", "APPROVE"],
            default="HOLD" if analysis.status != LoadStatus.OPTIMAL else "APPROVE",
            key=f"action_{record['inspection_id']}",
        )
        if st.button("Save action", width="stretch"):
            st.success(f"Action `{action}` recorded for {record['inspection_id']}.")

        try:
            synced = sync_unsynced_to_snowflake()
            if synced:
                st.caption(f"Synced {synced} inspection(s) to Snowflake.")
        except Exception as exc:  # noqa: BLE001
            st.caption(f"Snowflake sync skipped: {exc}")

st.divider()
st.caption(
    "Tip: open this page on your phone browser. Stand behind the truck with doors open "
    "and capture the full trailer interior."
)
