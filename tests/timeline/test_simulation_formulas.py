"""
Tests for simulation formulas.

PR-003b: Unit tests for population dynamics formulas including
logistic growth, multi-species growth, and carrying capacity calculations.
"""

import pytest

from app_timeline.simulation.formulas import (
    calculate_carrying_capacity,
    calculate_logistic_growth,
    calculate_multi_species_growth,
)


class TestLogisticGrowth:
    """Tests for calculate_logistic_growth formula."""

    def test_basic_growth(self):
        """Test basic logistic growth calculation."""
        N = 1000
        r = 0.05
        K = 10000

        new_N = calculate_logistic_growth(N, r, K)

        # Should grow (N < K)
        assert new_N > N
        # Should be less than or equal to K
        assert new_N <= K

    def test_growth_at_capacity(self):
        """Test logistic growth at carrying capacity."""
        N = 10000
        r = 0.05
        K = 10000

        new_N = calculate_logistic_growth(N, r, K)

        # Should remain stable at K (or very close due to rounding)
        assert new_N == N

    def test_growth_near_capacity(self):
        """Test growth slows as population approaches capacity."""
        K = 10000
        r = 0.05

        # Population at 50% of K
        N1 = 5000
        growth_at_50 = calculate_logistic_growth(N1, r, K) - N1

        # Population at 90% of K
        N2 = 9000
        growth_at_90 = calculate_logistic_growth(N2, r, K) - N2

        # Growth should be smaller near capacity
        assert growth_at_90 < growth_at_50

    def test_zero_population(self):
        """Test with zero initial population."""
        N = 0
        r = 0.05
        K = 10000

        new_N = calculate_logistic_growth(N, r, K)

        # Should remain zero (no growth from zero)
        assert new_N == 0

    def test_zero_carrying_capacity(self):
        """Test with zero carrying capacity."""
        N = 1000
        r = 0.05
        K = 0

        new_N = calculate_logistic_growth(N, r, K)

        # Should return zero (no capacity)
        assert new_N == 0

    def test_exceeding_capacity(self):
        """Test population above carrying capacity."""
        N = 12000
        r = 0.05
        K = 10000

        new_N = calculate_logistic_growth(N, r, K)

        # Should decrease toward K
        assert new_N < N
        # Should not exceed K
        assert new_N <= K

    def test_time_step_scaling(self):
        """Test that time_step scales growth appropriately."""
        N = 1000
        r = 0.05
        K = 10000

        # Full step
        growth_full = calculate_logistic_growth(N, r, K, time_step=1.0) - N

        # Half step
        growth_half = calculate_logistic_growth(N, r, K, time_step=0.5) - N

        # Half step should produce roughly half the growth
        assert abs(growth_half - growth_full / 2) < 10  # Allow small rounding error


class TestMultiSpeciesGrowth:
    """Tests for calculate_multi_species_growth formula."""

    def test_basic_multi_species_growth(self):
        """Test basic multi-species growth calculation."""
        populations = {"huum": 5000, "sint": 3000}
        growth_rates = {"huum": 0.004, "sint": 0.006}
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # Both species should grow
        assert new_pops["huum"] > populations["huum"]
        assert new_pops["sint"] > populations["sint"]

        # Total should not exceed K
        assert sum(new_pops.values()) <= K

    def test_proportional_scaling_at_capacity(self):
        """Test proportional scaling when total exceeds capacity."""
        populations = {"huum": 8000, "sint": 7000}  # Total = 15000
        growth_rates = {"huum": 0.05, "sint": 0.05}  # High growth
        K = 10000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # Total should be clamped to K (allow for rounding error)
        assert abs(sum(new_pops.values()) - K) <= 1

        # Should maintain rough proportions
        original_ratio = populations["huum"] / populations["sint"]
        new_ratio = new_pops["huum"] / new_pops["sint"] if new_pops["sint"] > 0 else 0

        # Ratios should be similar (within 20%)
        assert abs(new_ratio - original_ratio) / original_ratio < 0.2

    def test_species_with_zero_growth_rate(self):
        """Test species with zero growth rate."""
        populations = {"huum": 5000, "sint": 3000}
        growth_rates = {"huum": 0.004, "sint": 0.0}  # sint has no growth
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # huum should grow
        assert new_pops["huum"] > populations["huum"]

        # sint should remain stable
        assert new_pops["sint"] == populations["sint"]

    def test_missing_growth_rate(self):
        """Test species without defined growth rate."""
        populations = {"huum": 5000, "sint": 3000}
        growth_rates = {"huum": 0.004}  # sint rate not defined
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # huum should grow
        assert new_pops["huum"] > populations["huum"]

        # sint should remain stable (default rate = 0)
        assert new_pops["sint"] == populations["sint"]

    def test_zero_total_population(self):
        """Test with all populations at zero."""
        populations = {"huum": 0, "sint": 0}
        growth_rates = {"huum": 0.004, "sint": 0.006}
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # Should remain zero (no spontaneous generation)
        assert new_pops["huum"] == 0
        assert new_pops["sint"] == 0

    def test_zero_carrying_capacity(self):
        """Test with zero carrying capacity."""
        populations = {"huum": 5000, "sint": 3000}
        growth_rates = {"huum": 0.004, "sint": 0.006}
        K = 0

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # All populations should be zero
        assert new_pops["huum"] == 0
        assert new_pops["sint"] == 0

    def test_single_species(self):
        """Test with single species (should match calculate_logistic_growth)."""
        populations = {"huum": 5000}
        growth_rates = {"huum": 0.004}
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # Should grow
        assert new_pops["huum"] > populations["huum"]

        # Compare with direct logistic calculation
        expected = calculate_logistic_growth(5000, 0.004, K)
        assert new_pops["huum"] == expected

    def test_many_species(self):
        """Test with many species."""
        populations = {
            "huum": 5000,
            "sint": 3000,
            "mixed": 1000,
            "maken": 500
        }
        growth_rates = {
            "huum": 0.004,
            "sint": 0.006,
            "mixed": 0.005,
            "maken": 0.002
        }
        K = 20000

        new_pops = calculate_multi_species_growth(populations, growth_rates, K)

        # All should be present
        assert len(new_pops) == 4

        # Total should not exceed K
        assert sum(new_pops.values()) <= K


class TestCarryingCapacity:
    """Tests for calculate_carrying_capacity formula."""

    def test_basic_calculation(self):
        """Test basic carrying capacity calculation."""
        K_base = 10000
        C_t = 1.1  # Good environment
        I_t = 1.2  # Improved infrastructure
        L_t = 1.0  # Average location

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should be K_base × 1.1 × 1.2 × 1.0 = 13,200
        assert K == 13200

    def test_all_factors_at_one(self):
        """Test with all factors at 1.0 (neutral)."""
        K_base = 10000
        C_t = 1.0
        I_t = 1.0
        L_t = 1.0

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should equal base capacity
        assert K == K_base

    def test_poor_environment(self):
        """Test with poor environmental factor."""
        K_base = 10000
        C_t = 0.8  # Poor environment
        I_t = 1.0
        L_t = 1.0

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should be reduced
        assert K == 8000

    def test_high_infrastructure(self):
        """Test with high infrastructure factor."""
        K_base = 10000
        C_t = 1.0
        I_t = 1.5  # Good infrastructure
        L_t = 1.0

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should be increased
        assert K == 15000

    def test_combined_factors(self):
        """Test with multiple factors varying."""
        K_base = 10000
        C_t = 0.9   # Slightly poor environment
        I_t = 1.3   # Good infrastructure
        L_t = 1.1   # Good location

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should be 10000 × 0.9 × 1.3 × 1.1 = 12,870
        assert K == 12870

    def test_very_low_factors(self):
        """Test with very low factors."""
        K_base = 10000
        C_t = 0.5   # Harsh environment
        I_t = 0.8   # Poor infrastructure
        L_t = 0.7   # Poor location

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Should be significantly reduced
        assert K == 2800

    def test_integer_rounding(self):
        """Test that result is properly rounded to integer."""
        K_base = 10000
        C_t = 1.15
        I_t = 1.25
        L_t = 1.05

        K = calculate_carrying_capacity(K_base, C_t, I_t, L_t)

        # Result should be integer
        assert isinstance(K, int)

        # Should be approximately 10000 × 1.15 × 1.25 × 1.05 = 15,093.75 → 15093
        assert K == 15093
