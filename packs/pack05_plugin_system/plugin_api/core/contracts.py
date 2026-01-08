import yaml

REQUIRED_FIELDS = [
    "name",
    "version",
    "entrypoint",
    "api_level",
]


class ContractViolation(Exception):
    pass


def validate_manifest(path: str):
    """
    Does this plugin have a proper manifest?
    """
    with open(path) as f:
        data = yaml.safe_load(f)

    for field in REQUIRED_FIELDS:
        if field not in data:
            raise ContractViolation(f"Missing required field: {field}")

    if not isinstance(data["api_level"], int):
        raise ContractViolation("api_level must be an integer")

    return True


def validate_api(plugin_obj, required_methods):
    """
    Ensure the plugin instance exposes the proper runtime API.
    """
    for method in required_methods:
        if not hasattr(plugin_obj, method):
            raise ContractViolation(f"Missing API method '{method}'")

    return True
