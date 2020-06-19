import os

try:
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from urlparse import urlparse, parse_qs


def decompose_url(url):
    components = {
        "scheme": None,
        "host": None,
        "port": None,
        "username": None,
        "password": None,
        "auth_db": ""
    }

    result = urlparse(url)

    components["scheme"] = result.scheme
    components["host"] = result.hostname
    try:
        components["port"] = result.port
    except ValueError:
        raise RuntimeError("invalid port specified")
    components["username"] = result.username
    components["password"] = result.password

    try:
        components["auth_db"] = parse_qs(result.query)['authSource'][0]
    except KeyError:
        # no auth db provided, mongo will use the one we are connecting to
        pass

    return components


def compose_url(scheme=None,
                host=None,
                username=None,
                password=None,
                database=None,
                collection=None,
                port=None,
                auth_db=""):

    url = "{scheme}://"

    if username and password:
        url += "{username}:{password}@"

    url += "{host}"

    if database:
        url += "/{database}"

    if database and collection:
        url += "/{collection}"

    if port:
        url += ":{port}"

    url += auth_db

    return url.format(**{
        "scheme": scheme,
        "host": host,
        "username": username,
        "password": password,
        "database": database,
        "collection": collection,
        "port": port,
        "auth_db": ""
    })


def get_default_components():
    return decompose_url(os.environ["MONGO_URL"])
