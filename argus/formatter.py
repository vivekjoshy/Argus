from datetime import timedelta


class TimeDelta(timedelta):
    def __str__(self):
        _times = super(TimeDelta, self).__str__().split(":")
        if "," in _times[0]:
            _hour = int(_times[0].split(",")[-1].strip())
            if _hour:
                _times[0] += " hours" if _hour > 1 else " hour"
            else:
                _times[0] = _times[0].split(",")[0]
        else:
            _hour = int(_times[0].strip())
            if _hour:
                _times[0] += " hours" if _hour > 1 else " hour"
            else:
                _times[0] = ""
        _min = int(_times[1])
        if _min:
            _times[1] += " minutes" if _min > 1 else " minute"
        else:
            _times[1] = ""
        _sec = int(_times[2])
        if _sec:
            _times[2] += " seconds" if _sec > 1 else " second"
        else:
            _times[2] = ""
        return ", ".join([i for i in _times if i]).strip(" ,").title()
