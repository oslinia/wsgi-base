import os
import re

from ...http import request, response

http = ('form', 'url_file', 'url_for')


def form(name: str):
    value = request.form(name.strip(r'\'"'))

    if value is None:
        value = ''

    return value


def url_file(name: str):
    return response.url_file(name.strip(r'\'"'))


def url_for(params: str):
    args, kwargs = list(), dict()

    for i in params.split(','):
        item = i.lstrip()

        if item.startswith(("'", '"')):
            args.append(item.strip(r'\'"'))

        elif '=' in item:
            k, v = item.split('=')

            kwargs.update({k: v.strip(r'\'"')})

    if (url := response.url_for(*args, **kwargs)) is None:
        return str(url)

    return url


class Engine(object):
    __slots__ = ('templates', 'line', 'block')

    templates: str
    line: str
    block: dict[str, str]

    def raw_template(self, name: str | os.PathLike):
        filepath = os.path.abspath(os.path.join(self.templates, name))

        if os.path.isfile(filepath):
            if list_tuples := self.list_tuples(filepath, list()):
                self.line, self.block = '', dict()

                for tuples in list_tuples:
                    self.tuple_handler(tuples)

                for k, v in self.block.items():
                    self.line = re.sub(f"{{% {k} %}}", v, self.line)

                return self.line

            else:
                return 'Error reading file'

        return 'Template file not found'

    def list_tuples(self, filepath: str, list_tuples: list[list[tuple[str | None, str]]]):
        try:
            f = open(filepath, 'r')
            body = f.read()
            f.close()

            if extend := re.search(r'^(.*)({% extends [\'"][A-Za-z0-9_/.]+[\'"] %})(.*)(\s+)', body):
                body = re.sub(''.join(extend.groups()), '', body)

                if os.path.isfile(filepath := os.path.join(
                        self.templates, re.search(r'(?<=[\'"]).*(?=[\'"])', extend.group(2)).group()
                )):
                    list_tuples = self.list_tuples(filepath, list_tuples)

            if blocks := re.findall(r'({% block [A-Za-z0-9_]+ -*%})', body):
                tuples, prev = list(), None

                for block in blocks:
                    value, body = re.split(block, body, 1)

                    tuples.append((prev, value))

                    prev = block

                    if block.endswith('-%}'):
                        body = body.lstrip()

                tuples.append((prev, body))

            else:
                tuples = [(None, body)]

            list_tuples.append(tuples)

            return list_tuples

        except OSError:
            pass

    def tuple_handler(self, tuples: list[tuple[str | None, str]]):
        body, depth = list(), list()

        for block, line in tuples:
            if block is None:
                body.append(line)

            else:
                name = re.search(r'(?<= block )([A-Za-z0-9_]+)', block).group()
                key = name not in self.block.keys()

                if end_blocks := re.findall(r'({%-* endblock %})', line):
                    endings = list()

                    for end_block in end_blocks:
                        part, line = re.split(end_block, line, 1)

                        if end_block.startswith('{%-'):
                            part = part.rstrip()

                        endings.append(part)

                    endings.append(line)

                    body, depth, key = self.end_block(name, endings, depth, key, body)

                else:
                    depth.append(name)

                    if key:
                        body.append(f"{{% {name} %}}")

                    self.block[name] = self.add_super(name, line)

        self.line = f"{self.line}{''.join(body).rstrip()}"

    def end_block(self, name: str, endings: list[str], depth: list[str], key: bool, body: list[str]):
        self.block[name], i = self.add_super(name, endings.pop(0)), 0

        for ending in endings:
            if depth:
                current = depth.pop()

                if 0 == i:
                    if key:
                        ending, key = f"{{% {name} %}}{ending}", False

                else:
                    if current not in self.block.keys():
                        ending = f"{{% {current} %}}{ending}"

                self.block[current] = self.add_super(name, f"{self.block[current]}{ending}")

            else:
                if key:
                    body.append(f"{{% {name} %}}{ending}")

                else:
                    body.append(ending)

            i += 1

        return body, depth, key

    def add_super(self, name: str, line: str):
        if '{{ super() }}' in line:
            if name in self.block.keys():
                return re.sub(r'{{ super\(\) }}', self.block[name].rstrip(), line)

        return line
