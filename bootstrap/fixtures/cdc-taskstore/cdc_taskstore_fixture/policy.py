"""Generic unchanged validators and explicit unconfigured test slots."""
import re
ID = re.compile(r'[a-z0-9][a-z0-9-]{0,63}\Z')

SHA = re.compile(r'[0-9a-f]{40}\Z')

def fields(value, names, label):
    if not isinstance(value, dict) or set(value) != set(names.split()):
        raise ValueError(label + ' fields mismatch')

def identifier(value):
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ValueError('invalid identifier')

def project_for(value, project_id):
    matches = [p for p in value['projects'] if p['id'] == project_id]
    if len(matches) != 1:
        raise ValueError('unregistered project')
    return matches[0]

def validate_registry(*args,**kwargs):
    raise AssertionError("the original test must supply its registry fixture")
def validate_task(*args,**kwargs):
    raise AssertionError("task admission is outside this read-only qualification fixture")
