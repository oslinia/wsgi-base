import os
import re
from datetime import datetime
from typing import Any

from .engine import http, Engine


class Format(object):
    __slots__ = ('datetime',)

    def __init__(self, dt: datetime):
        self.datetime = dt

    def utc(self):
        return self.datetime.strftime('%d-%m-%Y')

    def usa(self):
        return self.datetime.strftime('%m-%d-%Y')

    def eng(self):
        return self.datetime.strftime('%d/%m/%Y')

    def rus(self):
        return self.datetime.strftime('%d.%m.%Y')

    def time(self):
        return self.datetime.strftime('%H:%M:%S')


class Template(Engine):
    __slots__ = ('template', 'key')

    key: str

    def __init__(self, name: str | os.PathLike):
        self.template = self.raw_template(name)

    def rendering(self, context: dict[str, Any] | None):
        if all_keys := re.findall(r'{{ ([A-Za-z0-9_|]+\(?[\s\'"A-Za-z0-9_=.,]*\)?) }}', self.template):
            keys = tuple() if context is None else context.keys()

            for self.key in all_keys:
                if self.key in keys:
                    self.replace(context[self.key])

                elif '|' in self.key:
                    value, funcs = context[(s := self.key.split('|'))[0]], s[1:]

                    for func in funcs:
                        if func in ('utc', 'usa', 'eng', 'rus', 'time'):
                            value = getattr(Format(value), func)()

                    if type(value) is not str:
                        value = 'value not string'

                    self.replace(value)

                elif '(' in self.key:
                    if r := re.findall(r'([A-Za-z0-9_]+)\(\s*([\'"A-Za-z0-9_=., ]+[\'"])\s*\)', self.key):
                        name, args = r[-1]

                        if name in http:
                            self.replace(getattr(engine, name)(args))

        return self.template

    def replace(self, value: str):
        self.template = self.template.replace('{{ %s }}' % self.key, value)
