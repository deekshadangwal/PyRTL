import random
import unittest

import pyrtl
import pyrtl.rtllib.testingutils as utils
from pyrtl.rtllib import multipliers, adders


class TestWallace(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # this is to ensure reproducibility
        random.seed(777906376)

    def setUp(self):
        pyrtl.reset_working_block()

    def mult_t_base(self, len_a, len_b, **mult_args):
        # Creating the logic nets
        a, b = pyrtl.Input(len_a, "a"), pyrtl.Input(len_b, "b")
        product = pyrtl.Output(name="product")
        product <<= multipliers.tree_multiplier(a, b, **mult_args)

        self.assertEquals(len(product), len_a + len_b)

        # creating the testing values and the correct results
        xvals = [int(random.uniform(0, 2**len_a-1)) for i in range(20)]
        yvals = [int(random.uniform(0, 2**len_b-1)) for i in range(20)]
        true_result = [i * j for i, j in zip(xvals, yvals)]

        # Setting up and running the tests
        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.Simulation(tracer=sim_trace)
        for cycle in range(len(xvals)):
            sim.step({a: xvals[cycle], b: yvals[cycle]})

        # Extracting the values and verifying correctness
        multiplier_result = sim_trace.trace[product]
        self.assertEqual(multiplier_result, true_result)

        sim_trace = pyrtl.SimulationTrace()
        sim = pyrtl.FastSimulation(tracer=sim_trace)
        for cycle in range(len(xvals)):
            sim.step({a: xvals[cycle], b: yvals[cycle]})

        multiplier_result = sim_trace.trace[product]
        self.assertEqual(multiplier_result, true_result)

    def test_trivial_case(self):
        self.mult_t_base(1, 5)

    def test_trivial_case_2(self):
        self.mult_t_base(2, 1)

    def test_trivial_case_3(self):
        self.mult_t_base(1, 1)

    def test_wallace_tree_1(self):
        self.mult_t_base(5, 7)

    def test_wallace_tree_2(self):
        self.mult_t_base(2, 9)

    def test_dada_tree(self):
        self.mult_t_base(5, 10, reducer=adders.dada_reducer)

    def test_fma_1(self):
        wires, vals = utils.make_wires_and_values(exact_bitwidth=10, num_wires=3)
        test_w = multipliers.fused_multiply_adder(wires[0], wires[1], wires[2], False,
                                                  reducer=adders.dada_reducer,
                                                  adder_func=adders.ripple_add)
        self.assertEqual(len(test_w), 20)
        outwire = pyrtl.Output(21, "test")
        outwire <<= test_w

        out_vals = utils.sim_and_ret_out(outwire, wires, vals)
        true_result = [vals[0][cycle] * vals[1][cycle] + vals[2][cycle]
                       for cycle in range(len(vals[0]))]
        self.assertEqual(out_vals, true_result)

    def test_gen_fma_1(self):
        wires, vals = utils.make_wires_and_values(max_bitwidth=8, num_wires=8)
        # mixing tuples and lists solely for readability purposes
        mult_pairs = [(wires[0], wires[1]), (wires[2], wires[3]), (wires[4], wires[5])]
        add_wires = (wires[6], wires[7])

        outwire = pyrtl.Output(name="test")
        outwire <<= multipliers.generalized_fma(mult_pairs, add_wires, signed=False)

        out_vals = utils.sim_and_ret_out(outwire, wires, vals)
        true_result = [vals[0][cycle] * vals[1][cycle] + vals[2][cycle] * vals[3][cycle] +
                       vals[4][cycle] * vals[5][cycle] + vals[6][cycle] + vals[7][cycle]
                       for cycle in range(len(vals[0]))]
        self.assertEqual(out_vals, true_result)

