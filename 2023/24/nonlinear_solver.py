import numpy as np
from scipy.optimize import fsolve


# for a given variable r, this function returns F(r)
# if r is the solution of the nonlinear system, then
# F(r)=0
# F can be interpreted as the residual
# r elements are: [x, y, z, u, v, w, t1, t2, t3]
def rock_equations(r):
    F = np.zeros(9)
    F[0] = 19 - 2*r[6] - r[0] - r[6]*r[3]
    F[1] = 13 + r[6] - r[1] - r[6]*r[4]
    F[2] = 30 - 2*r[6] - r[2] - r[6]*r[5]
    F[3] = 18 - r[7] - r[0] - r[7]*r[3]
    F[4] = 19 - r[7] - r[1] - r[7]*r[4]
    F[5] = 22 - 2*r[7] - r[2] - r[7]*r[5]
    F[6] = 20 - 2*r[8] - r[0] - r[8] * r[3]
    F[7] = 25 - 2*r[8] - r[1] - r[8] * r[4]
    F[8] = 34 - 4*r[8] - r[2] - r[8] * r[5]

    return F


# generate an initial guess
initialGuess=np.zeros(9)

# solve the problem
solutionInfo=fsolve(rock_equations,initialGuess,full_output=True)
print(solutionInfo)
solution = solutionInfo[0]
print(f"Answer: {solution}")
print(f"x={round(solution[0])}")
print(f"y={round(solution[1])}")
print(f"z={round(solution[2])}")
print(f"u={round(solution[3])}")
print(f"v={round(solution[4])}")
print(f"w={round(solution[5])}")
print(f"t1={round(solution[6])}")
print(f"t2={round(solution[7])}")
print(f"t3={round(solution[8])}")