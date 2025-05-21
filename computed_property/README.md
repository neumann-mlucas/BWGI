### Computed Property

The goal is to recreate this mechanism for Python objects, in memory. To do
this, write a decorator called computed_property, analogous to property. The
computed_property decorator should accept multiple attributes on which it
depends and cache the value of the property as long as the values of these
attributes remain unchanged.


#### Usage

```python
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
```


#### Extra

If returning a property is not a requirement, it would be easy to add the functionality of functools.cache

```python
def cache_with_dependencies(*dependencies: str) -> Callable:
    """
    Decorator that creates a cached property whose value depends on other attributes.

    This decorator creates a property that computes its value based on specified
    dependent attributes. The value is cached and only recalculated when any of
    the dependent attributes change or when the arguments to the property method
    (if any) change.

    Not implementing a dependency graph, so the dependencies are not recursive.
    Not handling all combinations of args and kwargs to keep the example simple.
    Args and Dependencies do not support mutable types to keep the example simple.
    """

    def inner_decorator(fn: Callable) -> property:
        # using closures state to store the current state and cache
        state: frozenset[tuple] = frozenset()
        cache: dict[frozenset, Any] = {}

        def wrapped(*args, **kwargs) -> Callable:
            nonlocal state, cache
            # assumes it will only be used in method
            self = args[0]

            # immutable, hashable and order independent
            curr_state = frozenset(
                (attr, getattr(self, attr))
                for attr in dependencies
                if hasattr(self, attr)
            )
            curr_args = frozenset([*enumerate(args[1:]), *kwargs.items()])

            if curr_state != state or curr_args not in cache:
                state = curr_state
                cache[curr_args] = fn(*args, **kwargs)

            return cache[curr_args]

        return wrapped

    return inner_decorator
```
