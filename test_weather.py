import pytest
import weather

def test_get_weather():
    nyc_lat = 40.827232375361085
    nyc_long = -73.9466391392184
    assert weather._get_weather_info_by_coord(nyc_lat, nyc_long)

def test_heading():
    assert weather._parse_compass_heading(5) == "N"
    assert weather._parse_compass_heading(355) == "N"
    assert weather._parse_compass_heading(20) == "NNE"
    assert weather._parse_compass_heading(40) == "NE"
    assert weather._parse_compass_heading(60) == "ENE"
    assert weather._parse_compass_heading(90) == "E"
    assert weather._parse_compass_heading(110) == "ESE"
    assert weather._parse_compass_heading(140) == "SE"
    assert weather._parse_compass_heading(150) == "SSE"
    assert weather._parse_compass_heading(190) == "S"
    assert weather._parse_compass_heading(195) == "SSW"
    assert weather._parse_compass_heading(225) == "SW"
    assert weather._parse_compass_heading(240) == "WSW"
    assert weather._parse_compass_heading(260) == "W"
    assert weather._parse_compass_heading(300) == "WNW"
    assert weather._parse_compass_heading(325) == "NW"
    assert weather._parse_compass_heading(345) == "NNW"

def test_kelvin_conversion():
    assert weather._k_to_f(0) == -459.67
    assert weather._k_to_f(255.372) == 0
    assert weather._k_to_f(273.15) == 32
    assert weather._k_to_f(294.261) == 70
    assert weather._k_to_f(373.15) == 212

def test_mps_to_mph():
    assert weather._mps_to_mph(0) == 0
    assert weather._mps_to_mph(1) == 2.24
    assert weather._mps_to_mph(100) == 223.7

def test_make_ordinal():
    assert weather._make_ordinal(1) == "1st"
    assert weather._make_ordinal(2) == "2nd"
    assert weather._make_ordinal(3) == "3rd"
    assert weather._make_ordinal(4) == "4th"
    assert weather._make_ordinal(0) == "0th"
    assert weather._make_ordinal(11) == "11th"
    assert weather._make_ordinal(12) == "12th"
    assert weather._make_ordinal(13) == "13th"
    assert weather._make_ordinal(14) == "14th"
    assert weather._make_ordinal(10) == "10th"
    assert weather._make_ordinal(112) == "112th"
    assert weather._make_ordinal(-5) == "-5th"