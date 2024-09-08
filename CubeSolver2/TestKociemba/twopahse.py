import twophase.solver  as sv
import re

cubestring = 'DDUUURLRRFBRDRLFUFBFURFRBDDLBRFDFDUURLULLUFLDBFBDBBLBL'#'DUUBULDBFRBFRRULLLBRDFFFBLURDBFDFDRFRULBLUFDURRBLBDUDL'
t = 20
s = sv.solve(cubestring,0,t)
#s = re.sub(r'\s*\([^)]*\)', '', s)
print(s)