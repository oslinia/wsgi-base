import sys
from datetime import datetime, timedelta, timezone

now: datetime
timestamp: float

delta: "Delta"


def setup(time_zone: str | None):
    setattr(Delta, 'true', False)

    if time_zone is not None and ':' in time_zone:
        sign = '+'

        if time_zone.startswith(('-', '+')):
            if '-' == time_zone[0]:
                sign = '-'

            time_zone = time_zone[1:]

        hour, minute = (int(t) for t in time_zone.split(':'))

        if 0 != hour or 0 != minute:
            second = f"{sign}{hour * 60 * 60 + minute * 60}"

            for attr, value in (('true', True), ('delta', eval(second))):
                setattr(Delta, attr, value)

    setattr(sys.modules[__name__], 'delta', Delta())


class Delta(object):
    __slots__ = ('true', 'delta')

    true: bool
    delta: int

    def datetime(self, dt: datetime):
        if self.true:
            return dt + timedelta(seconds=self.delta)

        return dt

    def timestamp(self, ts: float):
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)

        return self.datetime(dt)
