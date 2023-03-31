import re
import logging
from datetime import datetime
from typing import Optional

REGEXES = [
    (r".*(20[0-2][0-9][0|1][0-9][0-3][0-9]?).*", "%Y%m%d"),       # 20160611
    (r".*(20[0-2][0-9]-[0|1][0-9]-[0-3][0-9]?).*", "%Y-%m-%d"),   # 2016-06-11
    (r".*(2[0-3]-[0|1][0-9]-[0-3][0-9]?).*", "%y-%m-%d"),         # 20-12-05
    (r".*([0-3][0-9]\.[0|1][0-9]\.20[0-2][0-9]?).*", "%d.%m.%Y")  # 30.04.2020
]

logger = logging.getLogger(__name__)


def parse_date(text: str) -> Optional[datetime]:
    result = None
    for regex, fmt in REGEXES:
        re_result = re.search(regex, text)
        if re_result and re_result.groups():
            try:
                result = datetime.strptime(re_result.groups()[0], fmt)
                break
            except Exception as ex:
                logger.exception("Couldn't parse: " + str((re_result.groups()[0], fmt)))
    return result

