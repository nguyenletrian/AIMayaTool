from __future__ import absolute_import
import unittest
from aimayatool.tools.scene import rope_weights
class RopeWeightsTests(unittest.TestCase):
 def test_pairs(self):
  self.assertEqual(rope_weights.normalize_pairs("a\n\nb","x\ny"),[("a","x"),("b","y")])
  self.assertRaises(ValueError,rope_weights.normalize_pairs,["a"],["x","y"])
 def test_roll(self):
  w=rope_weights.weights("roll",3,1,0)
  self.assertEqual(w[0],{"start":2.0/3.0,"end":1.0/3.0,"destination":0.0,"orient_reference":1.0,"orient_destination":0.0})
  self.assertEqual(w[2]["destination"],1.0)
 def test_straight_and_zero(self):
  w=rope_weights.weights("straight",3,2,0)
  self.assertEqual(w[1]["start"],1.0/3.0); self.assertEqual(w[1]["end"],2.0/3.0)
  self.assertRaises(ValueError,rope_weights.weights,"straight",3,-1,0)
if __name__=="__main__": unittest.main()
