

class WeatherStation:

    def __init__(self, wmoid, lat, lon, hgt):
        self.wmoid = wmoid

        self.lat = lat
        self.lon = lon
        self.hgt = hgt


    def __str__(self):
        return "WeatherStation (wmoid:%s, lat:%d, lon:%d, hgt:%d)" % (self.wmoid, self.lat, self.lon, self.hgt)