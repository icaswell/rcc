"""Whenever a new object is made, register its name.

The principle purpose of this is for debugging. And it has helped me many a time!
"""
import random

NAME_REGISTRY = set()

def get_unique_name(base):
    unique_name = f"{base}_{len(NAME_REGISTRY)}"
    return unique_name

def register_unique_name(base):
    unique_name = get_unique_name(base)
    register_name(unique_name)
    return unique_name

def register_name(name):
    # should be called in init function of any object.
    if name in NAME_REGISTRY:
        raise ValueError(f"Duplicate name '{name}' can't be added to registry!")
    NAME_REGISTRY.add(name)

def random_string():
    return ''.join(random.choices('qwertyuiopasdfghjklzxcvbnm', k=8))

def reset_name_registry():
  global NAME_REGISTRY
  NAME_REGISTRY = set()


ADJECTIVES = "Thoraic Magnificent Ineffable".split()
NOUNS = "Teapot Spoon Rock".split()
ANIMALS = "Badger Wombat Ant Human".split()
def get_glorious_name():
    name = f"{random.choice(ADJECTIVES)} {random.choice(NOUNS)}-{random.choice(ANIMALS)}"
    register_name(name)
    return name
