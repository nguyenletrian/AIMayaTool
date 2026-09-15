from __future__ import absolute_import

from aimayatool.tools.setup.controls import build_curve_create_kwargs, create_curve_from_shape_data, normalize_curve_shape_data


def run():
    data = {"degree": 3, "form": 2, "pointData": {"cv[3]": [3, 0, 0], "cv[1]": [1, 0, 0], "cv[0]": [0, 0, 0], "cv[2]": [2, 0, 0]}, "knots": [0, 0, 0, 1, 1, 1]}
    spec = normalize_curve_shape_data(data)
    assert spec["degree"] == 3 and spec["form"] == 2
    assert spec["points"] == ((0.0,0.0,0.0),(1.0,0.0,0.0),(2.0,0.0,0.0),(3.0,0.0,0.0))
    kwargs = build_curve_create_kwargs(data)
    assert kwargs["degree"] == 3 and kwargs["periodic"] is True and kwargs["knot"] == [0.0,0.0,0.0,1.0,1.0,1.0]
    class FakeCmds(object):
        def curve(self, **values): self.values = values; return "curve1"
    fake = FakeCmds(); result = create_curve_from_shape_data(data, name="AS_CTRL", cmds_module=fake)
    assert result == "curve1" and fake.values["name"] == "AS_CTRL" and fake.values["periodic"] is True
    for invalid in ({"degree":0,"points":[[0,0,0]]},{"degree":3,"points":[[0,0,0],[1,0,0]]}):
        try: normalize_curve_shape_data(invalid)
        except ValueError: pass
        else: raise AssertionError("Expected ValueError")
    print("CONTROL_SHAPE_AS_PYTHON_SMOKE_OK")
    return True


if __name__ == "__main__": run()
