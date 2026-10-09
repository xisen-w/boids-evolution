"""Observed Python function calls; optional shape-preserving return intervention.

This is measurement instrumentation, not a security boundary or a complete call graph.
Only installed in the grader, never in the model environment. v0.3 also wraps
ordinary Python instance/static/class methods and property accessors. Native C
calls, arbitrary dynamic callbacks and generator iteration are not complete.
"""

import atexit
import contextlib
import contextvars
import functools
import importlib.abc
import importlib.machinery
import inspect
import json
import os
import sys

COUNTS = {}
EDGE = os.environ.get("BOIDS_ABLATE_EDGE", "")
SERVICE_ROOT = contextvars.ContextVar("boids_service_root", default=None)


@contextlib.contextmanager
def service_entry(namespace):
    """Attribute the judge's entry call to the package whose adapter is tested.

    A direct re-export executes the provider function without any intervening
    code in the publishing package. Preserve that actual provider as the callee,
    but identify the served publication rather than the judge as the caller.
    """
    token = SERVICE_ROOT.set(namespace)
    try:
        yield
    finally:
        SERVICE_ROOT.reset(token)


def perturb(value):
    if isinstance(value, bool):
        return not value, True
    if isinstance(value, (int, float)):
        return (0 if value != 0 else 1), True
    if isinstance(value, str):
        return ("__ablated__" if not value else ""), True
    if isinstance(value, list):
        items = [perturb(x) for x in value]
        return [x[0] for x in items], any(x[1] for x in items)
    if isinstance(value, dict):
        items = {k: perturb(v) for k, v in value.items()}
        return {k: v[0] for k, v in items.items()}, any(v[1] for v in items.values())
    return value, False


def wrap(function, module, name):
    @functools.wraps(function)
    def observed(*args, **kwargs):
        frame = inspect.currentframe().f_back
        caller = frame.f_globals.get("__name__", "unknown")
        service_entry_call = caller == "__main__" and SERVICE_ROOT.get() is not None
        if service_entry_call:
            caller = SERVICE_ROOT.get()
        if frame.f_code.co_filename.startswith("/workspace/"):
            caller = "consumer"
        del frame
        edge = f"{caller}->{module}.{name}"
        row = COUNTS.setdefault(edge, dict(calls=0, mutated=0, exceptions=0, service_entries=0))
        row["calls"] += 1
        row["service_entries"] += int(service_entry_call)
        try:
            value = function(*args, **kwargs)
        except BaseException:
            row["exceptions"] += 1
            raise
        if edge == EDGE:
            value, changed = perturb(value)
            row["mutated"] += int(changed)
        return value

    return observed


class Loader(importlib.abc.Loader):
    def __init__(self, wrapped, name):
        self.wrapped, self.name = wrapped, name

    def create_module(self, spec):
        return self.wrapped.create_module(spec)

    def exec_module(self, module):
        self.wrapped.exec_module(module)
        for name, value in list(vars(module).items()):
            if inspect.isfunction(value) and value.__module__ == self.name:
                setattr(module, name, wrap(value, self.name, name))
            elif inspect.isclass(value) and value.__module__ == self.name:
                for method_name, method in list(vars(value).items()):
                    label = f"{name}.{method_name}"
                    if isinstance(method, staticmethod):
                        setattr(value, method_name, staticmethod(wrap(method.__func__, self.name, label)))
                    elif isinstance(method, classmethod):
                        setattr(value, method_name, classmethod(wrap(method.__func__, self.name, label)))
                    elif inspect.isfunction(method):
                        setattr(value, method_name, wrap(method, self.name, label))
                    elif isinstance(method, property):
                        accessors = [
                            wrap(fn, self.name, f"{label}.{suffix}") if fn else None
                            for fn, suffix in zip(
                                (method.fget, method.fset, method.fdel), ("get", "set", "del")
                            )
                        ]
                        setattr(value, method_name, property(*accessors, doc=method.__doc__))


class Finder(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith("published."):
            spec = importlib.machinery.PathFinder.find_spec(fullname, path, target)
            if spec and spec.loader and hasattr(spec.loader, "exec_module"):
                spec.loader = Loader(spec.loader, fullname)
            return spec


sys.meta_path.insert(0, Finder())


@atexit.register
def save():
    if COUNTS:
        try:
            with open(f"/trace/{os.getpid()}.json", "w") as stream:
                json.dump(COUNTS, stream)
        except OSError:
            pass
