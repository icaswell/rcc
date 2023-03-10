"""Whenever a new object is made, register its name.

The principle purpose of this is for debugging. And it has helped me many a time!
"""
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

def reset_name_registry():
  global NAME_REGISTRY
  NAME_REGISTRY = set()

