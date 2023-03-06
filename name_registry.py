import random

NAME_REGISTRY = set()

def register_name(name):
    # should be called in init function of any object.
    if "_copy" in name: return
    if name in NAME_REGISTRY:
        raise ValueError(f"Duplicate name '{name}' can't be added to registry!")
    NAME_REGISTRY.add(name)

def random_string():
    return ''.join(random.choices('qwertyuiopasdfghjklzxcvbnm', k=8))
