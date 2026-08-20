"""Unit tests for DockVision load analysis."""

from __future__ import annotations

from io import BytesIO

import numpy as np
from PIL import Image

from src.dock_vision.analyzer import analyze_truck_load
from src.dock_vision.schemas import LoadStatus


def _noisy_image(mean: int, seed: int) -> bytes:
    rng = np.random.default_rng(seed)
    arr = rng.normal(loc=mean, scale=35, size=(480, 640))
    arr = np.clip(arr, 0, 255).astype(np.uint8)
    image = Image.fromarray(arr, mode="L").convert("RGB")
    buffer = BytesIO()
    image.save(buffer, format="JPEG")
    return buffer.getvalue()


def test_darker_noisy_image_tends_to_higher_load_estimate() -> None:
    dark = analyze_truck_load(_noisy_image(55, seed=1))
    light = analyze_truck_load(_noisy_image(210, seed=2))
    assert dark.estimated_load_pct >= light.estimated_load_pct


def test_analysis_returns_valid_status() -> None:
    result = analyze_truck_load(_noisy_image(120, seed=3))
    assert result.status in LoadStatus
    assert 0 < result.estimated_load_pct <= 100
    assert 0 < result.confidence <= 1
