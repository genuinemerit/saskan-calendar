# import pytest
from app_calendar import get_wanderer_report


def test_wanderer_pos_bounds():
    wanderers = get_wanderer_report()
    for day in range(0, 200, 20):
        for w in wanderers:
            pos = w.pos(day)
            assert 0.0 <= pos < 1.0


def test_wanderer_visibility_logic():
    wanderers = get_wanderer_report()
    for w in wanderers:
        assert w.vis(0.5)
        assert not w.vis(0.95)
        assert not w.vis(0.02)
