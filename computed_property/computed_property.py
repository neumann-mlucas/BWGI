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
    the dependent attributes change

    Not implementing a dependency graph, so the dependencies are not recursive.
    Dependencies do not support mutable types to keep the example simple.
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


class ComputedProperty:
    """
    Decorator that creates a cached property whose value depends on other attributes.

    Using base example from the Python documentation:
    https://docs.python.org/3/howto/descriptor.html#properties
    """

    def __init__(self, *deps, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

        self.dependencies = deps
        self.state = frozenset()
        self.cache = None

    def __call__(self, fget):
        self.fget = fget
        self.__doc__ = fget.__doc__
        return self

    def __set_name__(self, owner, name):
        self.__name__ = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError

        # new cached property code goes here
        state = frozenset(
            (attr, getattr(obj, attr))
            for attr in self.dependencies
            if hasattr(obj, attr)
        )
        if self.state != state or self.cache is None:
            self.state = state
            self.cache = self.fget(obj)
        return self.cache

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(
            *self.dependencies,
            fget=fget,
            fset=self.fset,
            fdel=self.fdel,
            doc=self.__doc__,
        )

    def setter(self, fset):
        return type(self)(
            *self.dependencies,
            fget=self.fget,
            fset=fset,
            fdel=self.fdel,
            doc=self.__doc__,
        )

    def deleter(self, fdel):
        return type(self)(
            *self.dependencies,
            fget=self.fget,
            fset=self.fset,
            fdel=fdel,
            doc=self.__doc__,
        )


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

    @ComputedProperty("radius")
    def _diameter(self):
        print(f">>> Calculating Diameter: {self.radius * 2}")
        return self.radius * 2

    @_diameter.setter
    def _diameter(self, diameter):
        self.radius = diameter / 2

    @_diameter.deleter
    def _diameter(self):
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
