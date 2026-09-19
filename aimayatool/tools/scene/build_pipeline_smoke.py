from __future__ import absolute_import

from .build_pipeline import BuildStep, run_build_pipeline


def run():
    order = []
    def ok(name):
        order.append(name)
        return name.upper()
    def fail():
        order.append("fail")
        raise RuntimeError("expected failure")
    results = run_build_pipeline([BuildStep("one", ok, args=["one"]), BuildStep("two", ok, args=["two"])])
    assert order == ["one", "two"]
    assert [item["result"] for item in results] == ["ONE", "TWO"]
    order[:] = []
    results = run_build_pipeline([BuildStep("one", ok, args=["one"]), BuildStep("bad", fail), BuildStep("three", ok, args=["three"])])
    assert order == ["one", "fail"] and len(results) == 2 and results[-1]["status"] == "failed"
    order[:] = []
    results = run_build_pipeline([BuildStep("bad", fail), BuildStep("after", ok, args=["after"])], stop_on_error=False)
    assert order == ["fail", "after"] and results[-1]["status"] == "success"
    try:
        run_build_pipeline([object()])
        raise AssertionError("invalid step unexpectedly accepted")
    except TypeError:
        pass
    return "SCENE_BUILD_PIPELINE_BEHAVIOR_OK"


RESULT = run()
assert RESULT == "SCENE_BUILD_PIPELINE_BEHAVIOR_OK"
