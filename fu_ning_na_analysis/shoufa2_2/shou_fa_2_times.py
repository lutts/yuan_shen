from datetime import datetime


class Ys_Timestamp:
    FORMAT = "%H:%M:%S.%f"

    def __init__(self, timestamp_str):
        try:
            self.t = datetime.strptime(timestamp_str, Ys_Timestamp.FORMAT)
        except:
            self.t = None

    def __sub__(self, other):
        if self.t is None:
            return "None"

        if other.t is None:
            return "None"

        minus = False
        if self.t > other.t:
            diff = self.t - other.t
        else:
            diff = other.t - self.t
            minus = True

        seconds = diff.seconds
        ms = diff.microseconds / 1000000
        # print(diff)
        # print("seconds: ", seconds)
        # print("ms:", ms)
        diff = seconds + ms
        if minus:
            diff = 0 - diff

        return round(diff, 3)
    
timestamp_dict = {
    "AAXH4358": ["00:00:03.083", "00:00:04.885", "00:00:04.952", 
                 "00:00:07.235", "00:00:07.235", "00:00:09.168",
                 "00:00:11.068", "00:00:11.735", "00:00:11.818", "00:00:11.987", "00:00:14.220", "00:00:14.370",
                 "00:00:17.553", 
                 ]
}