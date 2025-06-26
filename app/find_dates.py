from pprint import pprint as pp
import core as cal

"""
Next:
- Find auspicious dates for events: full moons, new moons, max fixed stars, wanderers,
   the Spark, a Comet.
- Create functions to find auspicious dates within given ranges.
- Work with a range of about 3000 years:
    - Agents arrive ~ solar year 500
    - Animals awaken ~ solar year 1000
    - Great Migration arrival ~ solar year 2000
    - Story line begins ~ solar year 3400
    arrival of the Agents, awakening of the animals, arrival of the Great Migration
- Build a database for key dates.

- Re-work Saskan Solar Calendars. Do two of them - one Terpin, one Fatunik. The latter is
   based on mid-summer dates and uses a relatively complex set of rules to determine leap
   years. The Terpin calendar is simpler and uses a somewhat simpler set of rules to handle
   leap years. The Terpin calendar year begins on or about the Spring equinox. The Fatunik
   calendar year begins on or about mid-summer day.
- Terpin solar calendar:
    365 days / year
    Every, 132 years a 32-day festival brings us back to 365.2424, a +0.0002 overage
    To account for overage, the 35th Festival, every 4620 years, is a 31-day festival.
- Fatunik solar calendar:
    365 days / year
    Every 4 years (years divisible by 4) a 1-day festival brings us back close to 365.2422
    Every 100 years (years divisible by 4 and 100), the leap day is skipped.
    Except, every 400 years (years divisible by 4, 100 and 400) the leap day is added back.

- Re-work Saskan Lunar Calendars. Do three of them - Lunar A, Lunar B and Lunar C.
- Lunar A:  based on an average lunar cycle encompassing all the moons.
- Lunar B:  based on lunar cycle of the apparently largest moon.
- Lunar C:  based on the longest lunar lunar cycle.
"""


def basic_tests():
    """
    Check the basic functionality of the calendar module.
    There is a test for each of the functions.
    """
    print("\nOrdinal Number Conversion")
    for day in (1, 6, 7, 30, 93, 184, 275, 365, 366):
        ordinal_date = cal.ordinal(day)
        print(f"Input: {day} / Ordinal: {ordinal_date}")

    print("\nSanitize Epoch Pulse Count")
    for pulse in (-5, 0, 1, 2, 3, 73.4, 73.6, 10000, 500000, 67658432432434):
        sanitized_pulse = cal.sanitize_pulse_count_epoch(pulse)
        print(f"Input: {pulse} / Sanitized Epoch Pulse Count: {sanitized_pulse}")

    print("\nSanitize Daily Pulse Count")
    for pulse in (-5, 0, 1, 2, 3, 73.4, 73.6, 10000, 500000, 67658432432434):
        sanitized_pulse = cal.sanitize_pulse_count_day(pulse)
        print(f"Input: {pulse} / Sanitized Daily Pulse Count: {sanitized_pulse}")

    print("\nSanitize Astro Day")
    for day in (-5, 0, 1, 2.3, 3, 73.49, 73.9999, 10000, 439423.34981324871329784,
                439423.34987724871329784, 500000, 67658432432434):
        sanitized_day = cal.sanitize_astro_day(day)
        print(f"Input: {day} / Sanitized Astro Day: {sanitized_day}")

    print("\nSanitize Solar Turn")
    for turn in (-5, 0, 1, 2.3, 3, 73.499999, 73.5, 73.9999, 10000, 439423.34981324871329784,
                 439423.34987724871329784, 500000, 67658432432434):
        sanitized_turn = cal.sanitize_solar_turn(turn)
        print(f"Input: {turn} / Sanitized Solar Turn: {sanitized_turn}")

    print("\nSanitize Solar Day")
    for day in (-1, 0, 1, 365, 365.2422, 365.2423, 366, 366.5, 367, 36600):
        sanitized_day = cal.sanitize_solar_day(day)
        print(f"Input: {day} / Sanitized Solar Day: {sanitized_day}")

    print("\nAstro Day from Pulse Count")
    for pulse in (-5, 0, 1, 2.3, 3, 73.499999, 73.5, 73.9999, 10000, 439423.34981324871329784,
                  439423.34987724871329784, 500000, 67658432432434,
                  86400 * 30, 86400 * 365.2422, 86400 * 100000, (86400 * 100000) + 1,
                  (86400 * 100000) - 1):
        astro_day = cal.get_astro_day_from_pulse(pulse)
        print(f"Input: {pulse} / Astro Day from Pulse Count: {astro_day}")

    print("\nPulses Into Solar Day")
    for day in (-1, 0, 1, 2.456, 568.0003, 365.0, 365.2422, 365.2423,
                365.9999, 366.0, 1.9999999999):
        pulses = cal.get_pulses_into_solar_day(day)
        print(f"Input: {day} / Pulses into Solar Day: {pulses}")

    print("\nPulses To Astro Day")
    for day in (-1, 0, 1, 2, 3, 10, 2.456, 568.0003, 365.0, 365.2422, 365.2423,
                365.9999, 366.0, 1.9999999999, 366000000):
        pulses = cal.get_pulses_to_astro_day(day)
        print(f"Input: {day} / Pulses to Astro Day: {pulses}")

    print("\nSolar Day from Pulses")
    for pulse in (-5, 0, 1, 2.3, 3, 73.499999, 73.5, 73.9999, 10000, 439423.34981324871329784,
                  439423.34987724871329784, 500000, 67658432432434,
                  86400 * 30, 86400 * 365.2422, 86400 * 100000, (86400 * 100000) + 1,
                  (86400 * 100000) - 1,
                  (86400 * 10000000),
                  (86400 * 365.2422) + 1000):
        solar_day = cal.get_solar_day_from_pulse(pulse)
        print(f"Input: {pulse} / Solar Day from Pulses: {solar_day}")

    print("\nSolar Month from Solar Day")
    for day in (-10, 0, 1, 30, 30.43685, 30.5, 31,
                60, 61, 360, (30.43685 * 11) + 1,
                365.2422):
        solar_month = cal.get_solar_month(day)
        print(f"Input: {day} / Solar Month: {solar_month}")

    print("\nAstro Turn from Astro Day")
    for day in (-10, 0, 1, 2.3, 3, 73.499999, 73.5,
                73.9999, 10000, 439423.34981324871329784,
                439423.34987724871329784, 500000,
                67658432432434, 86400 * 30,
                86400 * 365.2422, 86400 * 100000,
                (86400 * 100000) + 1, (86400 * 100000) - 1):
        astro_turn = cal.get_astro_turn(day)
        print(f"Input: {day} / Astro Turn: {astro_turn}")

    print("\nSolar Season from Solar Day")
    for day in (-1, 0, 1, 30,
                46, 46.5, 47,
                92.5, 93, 93.5, 94,
                137.5, 138, 138.3,
                183.6, 184, 184.3,
                229, 229.5, 230,
                274.9, 275, 275.1, 275.2, 275.3, 275.4,
                320.2, 320.5, 320.7,
                366):
        season = cal.get_solar_season(day)
        print(f"Input: {day} / Solar Season: {season}")

    print("\nAstro Events from Astro Day")
    for day in (-5, 0, 1, 1.0, 1.4434, 1.56,
                77, 78.999, 182621):
        events = cal.get_astro_events(day)
        print(f"Input: {day} / Astro Events: {events}")


def find_moon_phases():
    """
    Test to ascertain moon phases on a given astronomical day.
    """
    print("\nMoon Phases from Astro Day")
    for day in (1, 5.55, 6.55, 6.66, 7.55,
                11.1, 18, 18.9, 19.0, 20.0,
                22.7, 27.3, 30, 31, 32, 33,
                33.5, 35, 36, 45, 45.0,
                54.2, 56, 57, 58, 59, 60
                ):
        phases = cal.get_moon_phases(day)
        pp(('phases', phases))


def create_kanka_spin_data():
    """
    Create a Kanka spin data file for the Saskan calendar.
    The file is used to create chaotic events in Kanka's rotation.
    Verify by examining ./kanka_spin_data.json
    """
    cal.seed_kanka_chaos()


def find_solar_days():
    """
    Test to ascertain astronomical events on a given solar day.
    A "solar day" is a day in the solar calendar, which is based on Gavor's true orbit
       around Fatune (365.2544 rotations) during one revolution ("turn" or year),
       not based on on any particular calendar system.
    winter_solstice = 1
    spring_equinox = 93
    summer_solstice = 184
    autumn_equinox = 275
    Keep in mind that the solar day is forced to range from 1 to 365.2422 and may
    have up to 4 decimal places. There are no leap years in the solar calendar,
    It is neither the Astronomical day nor the Fatunik day.
    """
    for start_day in [1, 93, 184, 275]:
        print("\n====================================\n")
        # for adjust_day in (0, 45, 45.5, 46, 364, 365.25):
        for adjust_day in (0,):
            test_day = start_day + adjust_day
            solar_day = cal.sanitize_solar_day(test_day)
            print(f"solar day: {solar_day}")
            season = cal.get_season(solar_day)
            solar_month = cal.get_solar_month(solar_day)
            print(f'{season}, {solar_month}')
            moons = cal.get_moon_phases(solar_day)
            pp((moons))
            count_moons = cal.count_moon_phases(moons)
            pp((count_moons))
            stars = cal.get_star_context(solar_day)
            pp((stars))
            print(f"Fixed Stars Count: {len(stars['Fixed Stars'])}")
            pulses = cal.get_pulses_from_solar_day(solar_day)
            pp(('Pulses', pulses))
            saskan_time = cal.get_saskan_time_from_pulse(pulses)
            pp((saskan_time))
            wanderers = cal.get_wanderers(solar_day)
            pp((wanderers))
            wand_cnt = cal.count_visible_wanderers(wanderers)
            pp((wand_cnt))
            print("\n------------------------------------\n")


def find_auspicious_days():
    """
    Find days that are auspicious for various astronomical reasons.
    Notes:
    - 365.2422 * 5000 = 1826211.000 days in 5000 solar years
    """
    # Full moons
    for fm_count in range(6, 7):
        # start_year, end_year, full_moon_count
        moons = cal.find_full_moons(1, 5000, fm_count)
        pp((moons))


def find_astro_dates():
    """
    Test to ascertain astro turns.
    Then combine with the solar day to get the Astro date.
    winter_solstice = 1
    spring_equinox = 93
    summer_solstice = 184
    autumn_equinox = 275
    """
    for start_day in [1, 93, 184, 275]:
        print("\n====================================\n")
        for adjust_day in (0, 45, 45.5, 46,
                           364, 365.25, 365.5, 365.75, 366,
                           570, 600, 1000, 10000, 100000):
            test_day = start_day + adjust_day
            astro_day = cal.sanitize_astro_day(test_day)
            print("Start, Adjust, Test, Solar:\n" +
                  f"{start_day}, {adjust_day}, {test_day}, {astro_day}")
            print(cal.get_astro_turn(astro_day))
            pulses = cal.get_pulses_from_astro_day(astro_day)
            pp(('Total Pulses', pulses))
            solar_day = cal.get_solar_day_from_pulse(pulses)
            pp(('Solar Day', solar_day))


def find_fatunik_dates():
    """
    Test to make sure computation of Fatunik (solar) months, seasons and leaps is correct.
    The number passed in is the Astro epoch day, which counts starting from zero.
    The Fatunik epoch day starts with 1, so remember all the inputs will be incremented by
    1 when computing Fatunk dates.
    """
    for adjust in (0, 1, 5,
                   6, 34, 35,
                   36, 64, 65, 66,
                   364, 365, 366,
                   728, 729, 730,
                   1092, 1093, 1094, 1095,
                   1456, 1457, 1458, 1459, 1460, 1461):
        day = cal.FATUNIK_EPOCH_DAY + adjust
        astro = cal.AstroCalendar(day)
        astro_date = astro.get_astro_date()
        fatunik = cal.FatunikCalendar(day)
        fatunik_date = fatunik.get_date()
        info = astro_date | fatunik_date
        pp(info)
        print("\n====================================\n")


if __name__ == "__main__":
    # basic_tests()
    # find_moon_phases()
    create_kanka_spin_data()
    # find_solar_days()
    # find_auspicious_days()
    # find_astro_dates()
    # find_fatunik_dates()
