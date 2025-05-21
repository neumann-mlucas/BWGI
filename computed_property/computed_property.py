"""
The goal is to recreate this mechanism for Python objects, in memory. To do
this, write a decorator called computed_property, analogous to property. The
computed_property decorator should accept multiple attributes on which it
depends and cache the value of the property as long as the values of these
attributes remain unchanged.

example:

class Circle:
    def __init__(self, radius=1):
        self.radius = radius

    @computed_property("radius")
    def diameter(self):
        return self.radius * 2

c = Circle()
c.diameter # computes value
c.diameter # get cached value
c.radius = 2
c.diameter # computes value
"""

from typing import Callable, Any


def computed_property(*dependencies: str) -> Callable:
    """
    Decorator that creates a cached property whose value depends on other attributes.

    Although the exercise calls for a reimplementation of the property decorator,
    returning a property object, avoids writing a custom property class (hack).

    This decorator creates a property that computes its value based on specified
    dependent attributes. The value is cached and only recalculated when any of
    the dependent attributes change or when the arguments to the property method
    (if any) change.

    Not implementing a dependency graph, so the dependencies are not recursive.
    dependencies do not support mutable types to keep the example simple.
    """

    def inner_decorator(fn: Callable) -> property:
        # using closures state to store the current state and cache
        state: frozenset[tuple] = frozenset()
        cache: Any = None

        def wrapped(*args, **kwargs) -> Callable:
            nonlocal state, cache
            # assumes it will only be used in method
            self = args[0]
            # check if obj state has changed
            # state should be immutable, hashable and order independent
            curr_state = frozenset(
                (attr, getattr(self, attr))
                for attr in dependencies
                if hasattr(self, attr)
            )
            if curr_state != state or cache is None:
                state = curr_state
                cache = fn(*args, **kwargs)
            return cache

        return property(wrapped)

    return inner_decorator


class Circle:
    def __init__(self, radius=1):
        self.radius = radius

    @computed_property("radius")
    def diameter(self):
        print(f">>> Calculating Diameter: {self.radius * 2}")
        return self.radius * 2

    @diameter.setter
    def diameter(self, diameter):
        self.radius = diameter / 2

    @diameter.deleter
    def diameter(self):
        self.radius = 0


def main():
    # small tests of computed_property behavior

    print(" - Creating Circle of Radius 1")
    c = Circle()
    print(f"1. Circle Diameter is {c.diameter}")
    print(f"2. Circle Diameter is {c.diameter}")
    print()

    print(" - Changing Circle Radius to 10")
    c.radius = 10
    print(f"1. Circle Diameter is {c.diameter}")
    print(f"2. Circle Diameter is {c.diameter}")
    print()

    print(" - Changing Circle Diameter to 40")
    c.diameter = 40
    print(f"1. Circle Diameter is {c.diameter}")
    print(f"2. Circle Diameter is {c.diameter}")
    print()

    print(" - Deleting Circle Diameter")
    del c.diameter
    print(f"1. Circle Diameter is {c.diameter}")
    print(f"2. Circle Diameter is {c.diameter}")
    print()


if __name__ == "__main__":
    main()
