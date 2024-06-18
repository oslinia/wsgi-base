import os

from .template.engine import Engine
from ..routing.urlmap import Link

dirname: str

urlpath: str
link: Link


def valid(url: str | None):
    if url is None:
        url = '/'

    elif '' == url:
        raise ValueError(
            "URL for static files cannot be empty."
        )

    elif not url.startswith('/'):
        raise ValueError(
            "URL for static files must begin with a slash '%s'." % url
        )

    elif not url.endswith('/'):
        raise ValueError(
            "URL for static files must end with a slash '%s'." % url
        )

    return url


def templates(template_folder: str | os.PathLike | None):
    if template_folder is None:
        template_folder = 'templates'

    setattr(Engine, 'templates', os.path.abspath(os.path.join(dirname, template_folder)))
