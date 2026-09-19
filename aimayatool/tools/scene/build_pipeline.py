from __future__ import absolute_import


class BuildStep(object):
    def __init__(self, name, action, args=None, kwargs=None):
        name = str(name or "").strip()
        if not name:
            raise ValueError("Build step name is required")
        if not callable(action):
            raise TypeError("Build step action must be callable")
        self.name, self.action = name, action
        self.args, self.kwargs = tuple(args or ()), dict(kwargs or {})

    def run(self):
        return self.action(*self.args, **self.kwargs)


def run_build_pipeline(steps, stop_on_error=True):
    """Run ordered BuildSteps and return deterministic per-step results."""
    results = []
    for index, step in enumerate(steps or []):
        if not isinstance(step, BuildStep):
            raise TypeError("Pipeline item {0} must be a BuildStep".format(index))
        try:
            value = step.run()
            results.append({"name": step.name, "status": "success", "result": value, "error": None})
        except Exception as exc:
            results.append({"name": step.name, "status": "failed", "result": None, "error": str(exc)})
            if stop_on_error:
                break
    return results
