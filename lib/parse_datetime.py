import re
from datetime import datetime

REGEXES = [
    (r".*(20[0-2][0-9][0|1][0-9][0-3][0-9]?).*", "%Y%m%d"),       # 20160611
    (r".*(20[0-2][0-9]-[0|1][0-9]-[0-3][0-9]?).*", "%Y-%m-%d"),   # 2016-06-11
    (r".*(2[0-3]-[0|1][0-9]-[0-3][0-9]?).*", "%y-%m-%d"),         # 20-12-05
    (r".*([0-3][0-9]\.[0|1][0-9]\.20[0-2][0-9]?).*", "%d.%m.%Y")  # 30.04.2020
]


def parse_datetime(text):
    result = None
    for regex, fmt in REGEXES:
        re_result = re.search(regex, text)
        if re_result and re_result.groups():
            result = datetime.strptime(re_result.groups()[0], fmt)
            break
    return result

