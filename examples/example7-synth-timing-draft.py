""" Example 7: Reduction and Speed Analysis

    After building a circuit, one might want to do some stuff to reduce the
    hardware into simpler nets as well as analyze various metrics of the
    hardware. This functionality is provided in the Passes part of PyRTL
    and will demonstrated here
"""


import pyrtl
from pyrtl.analysis import estimate

# --- Part 1: Timing Analysis ------------------------------------------------

# Timing and area usage are key considerations of any hardware block that one
# makes. PyRTL provides functions to do these opertions

# Creating a sample harware block
pyrtl.reset_working_block()
const_wire = pyrtl.Const(6, bitwidth=4)
in_wire2 = pyrtl.Input(bitwidth=4, name="input2")
out_wire = pyrtl.Output(bitwidth=5, name="output")
out_wire <<= const_wire + in_wire2


# Now we will do the timing analysis as well as print out the critical path

# Generating timing analysis information
timing_map = estimate.timing_analysis()
print("Pre Synthesis:")
estimate.print_max_length(timing_map)

# We are also able to print out the critical paths as well as get them
# back as an array.
critical_path_info = estimate.timing_critical_path(timing_map)

# --- Part 2: Area Analysis --------------------------------------------------

# PyRTL also provides estimates for the area that would be used up if the
# circuit was printed as an ASIC

logic_area, mem_area = estimate.area_estimation(tech_in_nm=65)
est_area = logic_area + mem_area
print("Estimated Area of block", est_area, "sq mm")
print()


# --- Part 3: Synthesis ------------------------------------------------------

# Synthesis is the operation of reducing the circuit into simpler components
# The base synthesis function breaks down the more complex logic operations
# into logic gates (keeps registers and memories intact) as well as reduces
# all combinatorial logic into ops that only use one bitwidth wires
#
# This synthesis allows for PyRTL to make optimizations to the net structure
# as well as prepares it for further transformations on the PyRT Toolchain

pyrtl.synthesize()

print("Pre Optimization:")
timing_map = estimate.timing_analysis()
estimate.print_max_length(timing_map)
for net in pyrtl.working_block().logic:
    print(str(net))
print()


# --- Part 4: Optimization ----------------------------------------------------

# PyRTL has functions built in to eliminate unnecessary logic from the
# circuit. These functions are all done with a simple call:
pyrtl.optimize()

# Now to see the difference
print("Post Optimization:")
timing_map = estimate.timing_analysis()
estimate.print_max_length(timing_map)

for net in pyrtl.working_block().logic:
    print(str(net))

# As we can see, the number of nets in the circuit were drastically reduced by
# the optimization algorithm.
