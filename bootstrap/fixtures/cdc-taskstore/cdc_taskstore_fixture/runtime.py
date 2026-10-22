"""Test dependency injection slot; the test supplies SDK module resolution."""
def module(name):
    raise AssertionError("fixture runtime.module must be supplied by the test")
