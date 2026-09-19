from __future__ import absolute_import
import unittest
from aimayatool.tools.scene import skin_joint_nearest_component as core

class SkinJointNearestComponentTests(unittest.TestCase):
    def test_greedy_assignment(self):
        d={("j1",0):1,("j1",1):5,("j2",0):2,("j2",1):1}
        self.assertEqual(core.greedy_assign(["j1","j2"],2,d),[{"joint":"j1","component_index":0,"distance":1.0},{"joint":"j2","component_index":1,"distance":1.0}])

    def test_stable_tie_order(self):
        d={("j1",0):1,("j1",1):1,("j2",0):1,("j2",1):1}
        self.assertEqual([(x["joint"],x["component_index"]) for x in core.greedy_assign(["j1","j2"],2,d)],[("j1",0),("j2",1)])

    def test_validation(self):
        self.assertRaises(ValueError,core.greedy_assign,["j1"],1,{})
        self.assertRaises(ValueError,core.greedy_assign,["j1","j1"],1,{("j1",0):1})
        self.assertRaises(ValueError,core.greedy_assign,["j1"],1,{("j1",0):-1})

if __name__=="__main__": unittest.main()
