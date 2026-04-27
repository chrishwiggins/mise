from fenics import *
# Create a mesh of a beam
mesh = UnitIntervalMesh(10)
# Define function space
V = FunctionSpace(mesh, 'P', 1)
# Define boundary condition
def boundary(x, on_boundary):
    return on_boundary
bc = DirichletBC(V, Constant(0), boundary)
# Define problem
u = TrialFunction(V)
v = TestFunction(V)
f = Constant(-5.0)
a = dot(grad(u), grad(v)) * dx
L = f * v * dx
# Compute solution
u = Function(V)
solve(a == L, u, bc)
# Plot solution
import matplotlib.pyplot as plt
plot(u)
plt.title('FEA: Displacement of Beam Under Load')
plt.show()

