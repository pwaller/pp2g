import os


def package(path):
    base = os.path.basename(path)
    if base.endswith(".py"):
        return base[:-len(".py")]
    return base


def to_camel(name: str) -> str:
    """
    Convert underscore_name to camelCaseName
    """
    parts = (p.capitalize() or "_" for p in name.split("_"))
    return "".join(parts)


def var_to_camel(name: str) -> str:
    camel = to_camel(name)
    return camel[0].lower() + camel[1:]
