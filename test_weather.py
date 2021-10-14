import pytest
import weather

def test_get_weather():
    assert weather._get_current_weather_by_zip() is not None

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
