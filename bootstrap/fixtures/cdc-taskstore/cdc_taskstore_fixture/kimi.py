"""Offline dependency injection slots; no Kimi/model/start implementation."""
OLD_TREE = "29b1a4fd71b1c83b30aa77812f6aa4627891cf52"
def validate_launch_task(*args, **kwargs):
    raise AssertionError("fixture launch validator must be supplied by the test")
