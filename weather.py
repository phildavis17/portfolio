"""
A weather report CLI. There are many like it, but this one is mine.
Uses OpenWeatherMap for weather data, and OpenStreetMap for reverse geocoding.
"""
import datetime
import json
import requests

from weather_secrets import OWM_API_KEY

# TODO: cached weather requests (time (10 min) and LAT/LONG (+/- some threshold))
# TODO: Today's weather
# TODO: exclude minutely
# TODO: evironment variable awareness for -location -units







DEFAULT_ZIP = "10031"
DEFAULT_COUNTRY_CODE = "US"


def _k_to_f(k: float) -> float:
    """Returns the supplied float converted from Kelvin to Farenheit."""
    return round((k-273.15) * 9/5 + 32, 3)

def _mps_to_mph(s: float) -> float:
    """Returns the supplied float converted from meters per second to miles per hour."""
    return round(s * 2.237, 2)

def _parse_compass_heading(heading: float) -> str:
    """Converts a supplied compas headinf float to a string describing direction."""
    points = {
        0: "N",
        1: "NNE",
        2: "NE",
        3: "ENE",
        4: "E",
        5: "ESE",
        6: "SE",
        7: "SSE",
        8: "S",
        9: "SSW",
        10: "SW",
        11: "WSW",
        12: "W",
        13: "WNW",
        14: "NW",
        15: "NNW",
    }
    return points[int((heading + 11.25) % 360 // 22.5)]

def _parse_beaufort_wind_speed(wind_speed: float) -> str:
    """Returns the description associated with the supplied wind speed on the Beaufort scale."""
    wind_descriptions = {
        1: "Light air",
        4: "Light breeze",
        8: "Gentle breeze",
        13: "Moderate breeze",
        19: "Fresh breeze",
        25: "Strong breeze",
        32: "Near gale",
        39: "Gale",
        47: "Strong gale",
        55: "Whole gale",
        64: "Storm force",
        75: "Hurricane force",
    }
    description = "Calm"
    for min_speed, desc in wind_descriptions.items():
        if wind_speed >= min_speed:
            description = desc
        else:
            break
    return description

def _make_ordinal(n: int) -> str:
    """Returns the supplied int as an ordinal number string."""
    oridnal_suffix = {
        "1": "st",
        "2": "nd",
        "3": "rd",
    }
    if str(n)[-1] in oridnal_suffix and not 10 < n % 100 < 14:
        return str(n) + oridnal_suffix[str(n)[-1]]
    return str(n) + "th"


def _get_time_from_timestamp(timestamp:int) -> str:
    """Converts an epoch based timestamp to a 12 hr HH:MM formatted time."""
    dt = datetime.datetime.fromtimestamp(timestamp)
    return f"{dt.hour % 12 or 12}:{dt.minute}"

def _get_long_date_from_timestamp(timestamp: int) -> str:
    """Returns a long date string from a timestamp."""
    dt = datetime.date.fromtimestamp(timestamp)
    return dt.strftime(f"%A, %B {_make_ordinal(dt.day)}")

def _get_short_date_from_timestamp(timestamp: int) -> str:
    """Returns a short date string from a timestamp."""
    dt = datetime.date.fromtimestamp(timestamp)
    return dt.strftime(f"{dt.month}/{dt.day}/%y")

def _get_weather_info_by_coord(lat: float, long: float, api_key=OWM_API_KEY) -> dict:
    """Requests weather info for the supplied lat long coordinates from the OpenWeatherMap API and returns the response as a JSON object."""
    weather_api_uri = f"https://api.openweathermap.org/data/2.5/onecall?lat={lat}&lon={long}&appid={api_key}"
    raw_response = requests.get(weather_api_uri)
    return json.loads(raw_response.text)

def _osm_reverse_lookup(lat: float, long: float):
    """Uses the OpenStreetMap API to reverse-geocode the supplied lat long coordinates."""
    osm_reverse_api_uri = f"https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={long}&zoom=10&format=jsonv2"
    osm_response = requests.get(osm_reverse_api_uri)
    return json.loads(osm_response.text)

class WeatherReport():
    """A class to parse, contain, and display weather information."""
    
    def __init__(self, lat:float, long:float) -> None:
        weather_dict = _get_weather_info_by_coord(lat, long)
        loc_dict = _osm_reverse_lookup(lat, long)
        self.loc_name = loc_dict["name"]
        self.input_data = weather_dict
        self.raw_current = self.input_data["current"]
        #self.raw_minutely = self.input_data["minutely"]
        self.raw_hourly = self.input_data["hourly"]
        self.raw_daily = self.input_data["daily"]
        if "alerts" in self.input_data:
            self.alerts = self.input_data["alerts"]
        else:
            self.alerts = ""
    
    def get_current_weather(self) -> str:
        """Returns a string describing current weather conditions."""
        desc = self.raw_current["weather"][0]["description"].capitalize()
        temp = self._generate_temp_report(int(_k_to_f(self.raw_current["temp"])),int(_k_to_f(self.raw_current["feels_like"])))
        humidity = self.raw_current["humidity"]
        wind = self._generate_wind_report(self.raw_current["wind_speed"], self.raw_current["wind_deg"])
        report = (
            f"Currently in {self.loc_name}: "
            f"{desc} | "
            f"{temp} | "
            f"{humidity}% humid | "
            f"{wind}"
        )
        return report

    def _generate_hourly_report(self, hourly_dict:dict) -> dict:
        """Returns a dict containing strings describing hourly weather conditions."""
        hourly_report_dict = {
            "desc": f'{hourly_dict["weather"][0]["description"].capitalize()}',
            "dt": f'{_get_time_from_timestamp(hourly_dict["dt"])}',
            "temp": f'{self._generate_temp_report(int(_k_to_f(hourly_dict["temp"])), int(_k_to_f(hourly_dict["feels_like"])))}',
            "humidity": f'{hourly_dict["humidity"]}% humidity',
            "wind": f'{self._generate_wind_report(_mps_to_mph(hourly_dict["wind_speed"]), hourly_dict["wind_deg"])}',
            "pop": f'{hourly_dict["pop"] * 100}% chance of precipitation',
        }
        return hourly_report_dict

    def get_hourly_weather(self) -> str:
        """Returns a string describing the hourly weather conditions for the next 24 hours."""
        raw_dicts = self.raw_hourly[:24]
        hourly_dicts = [self._generate_hourly_report(d) for d in raw_dicts]
        reports = self._format_hourly_reports(hourly_dicts)
        report_string = (
            f"Next 24 hours in {self.loc_name}:\n"
        )
        for report in [self._generate_hourly_report_string(report) for report in reports]:
            report_string += report + "\n"
        return report_string
    
    @classmethod
    def _format_hourly_reports(cls, reports: list) -> list:
        """A convenience method consolidating report formatting steps into a single call."""
        reports = cls._insert_repeat_characters(reports)
        reports = cls._enhance_repeat_characters(reports)
        return cls._pad_report_strings(reports)

    @staticmethod
    def _insert_repeat_characters(reports: list) -> list:
        """Replaces weather description strings with a repeat character if the condition has not changed from the previous instance."""
        skip_keys = {"temp", "humidity"}
        most_recent = {}
        for report in reports:
            if not most_recent:
                most_recent = {k:v for k, v in report.items()}
                continue
            for k, v in report.items():
                if k in skip_keys:
                    continue
                if v == most_recent[k]:
                    report[k] = "???"
                else:
                    most_recent[k] = v
        return reports
    
    @staticmethod
    def _enhance_repeat_characters(reports: list) -> list:
        """Replaces all but the last repeat character in a series with a different one, indicating continuity."""
        for i, report in enumerate(reports):
            if i == len(reports) - 1:
                break
            for k, v in report.items():
                if v == "???" and reports[i + 1][k] == "???":
                    report[k] = "???"
        return reports

    @staticmethod
    def _generate_hourly_report_string(weather_dict: dict) -> str:
        """Converts an hourly weather dict into a long string."""
        report = (
            f"  {weather_dict['dt']} | "
            f"{weather_dict['desc']} | "
            f"{weather_dict['temp']}| "
            f"{weather_dict['humidity']} | "
            f"{weather_dict['wind']} | "
            f"{weather_dict['pop']}"
        )
        return report

    @staticmethod
    def _pad_report_strings(report_list: list) -> list:
        """Adds empty characters to the values in a list of dicts until each value is as long as the longest value for that key."""
        # find max length of each report element
        max_dict = {k: 0 for k in report_list[0]}
        for k in max_dict:
            for report in report_list:
                max_dict[k] = max(max_dict[k], len(report[k]))
        # pad each element to match the longest instance
        for report in report_list:
            for k, v in report.items():
                report[k] = str.center(v, max_dict[k])
        return report_list

    def get_weekly_weather(self):
        dicts = [self._build_weekday_weather_dict(day) for day in self.raw_daily]
        str_list = self._construct_weekly_report(dicts)
        report = ""
        for weather_str in str_list:
            report += weather_str + "\n"
        return report
    
    @classmethod
    def _construct_weekly_report(cls, dicts_list: list) -> list:
        """A convenience method tying together the methods involved in constructing and formatting a weekly report."""
        padded = cls._pad_report_strings(dicts_list)
        return [cls._format_weekday_weather_dict(d) for d in padded]

    @classmethod
    def _build_weekday_weather_dict(cls, weekday_weather_dict) -> dict:
        report_dict = {
            "short_date": _get_short_date_from_timestamp(weekday_weather_dict['dt']),
            "long_date": _get_long_date_from_timestamp(weekday_weather_dict['dt']),
            "desc": weekday_weather_dict["weather"][0]["description"].capitalize(),
            "temp": cls._generate_temp_report(int(_k_to_f(weekday_weather_dict["temp"]["day"])), int(_k_to_f(weekday_weather_dict["feels_like"]["day"]))),
            "humidity": f"{weekday_weather_dict['humidity']}% humidity",
            "wind": _parse_beaufort_wind_speed(_mps_to_mph(weekday_weather_dict["wind_speed"])),
            "pop": f"{int(weekday_weather_dict['pop'] * 100)}% chance of precipitation"
        }
        return report_dict

    @classmethod
    def _format_weekday_weather_dict(cls, info_dict: dict) -> str:
        """Constructs a string describing the weather conditions for on day in a week."""
        report_str = (
            f"{info_dict['long_date']}: "
            f"{info_dict['desc']} | "
            f"{info_dict['temp']} | "
            f"{info_dict['humidity']} | "
            f"{info_dict['wind']} | "
            f"{info_dict['pop']}"
        )
        return report_str

    @staticmethod
    def _generate_temp_report(temp:int, feel: int) -> str:
        """Returns a string describing temperature conditions."""
        report_str = f"{temp}??"
        if feel - temp > 3:
            report_str = f"Feels like {feel}??"
        return report_str
   
    @staticmethod
    def _generate_wind_report(wind_speed: float, wind_dir: int) -> str:
        """Returns a string describing wind conditions."""
        wind_description = _parse_beaufort_wind_speed(_mps_to_mph(wind_speed))
        if wind_speed < 1:
            return wind_description
        wind_description += f", {_parse_compass_heading(wind_dir)}"
        return wind_description


if __name__ == "__main__":
    seattle_zip = 98101
    nyc_lat = 40.827232375361085
    nyc_long = -73.9466391392184
    hudson_lat = 42.251954298905055
    hudson_long = -73.79160367431743
    teaneck_lat = 40.88573010263205 
    teaneck_long = -74.01985647117358
    cr_lat = 41.840757350547
    cr_long = -94.65589705807416
    #loc = reverse_geocoder.search((lat, long))
    weather = WeatherReport(nyc_lat, nyc_long)
    #print(weather.get_hourly_weather())
    print(weather.get_weekly_weather())






"""
Next 24 hours in New York:
  8:00 | Overcast clouds | 70?? | 56% humidity | Light breeze, NNW | 10% chance of precip
  9:00 |       ???         | 68?? | 58% humidity |       Calm        |         ???
 10:00 |  Broken clouds  | 65?? | 57% humidity |         ???         |         ???
 11:00 | Overcast Clouds | 63?? | 57% humidity |         ???         |         ???
"""
