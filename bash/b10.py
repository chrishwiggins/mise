from pydy.system import System
from sympy import symbols
# Define symbols
q, u = symbols('q u')
m, g, k = symbols('m g k')
# Define equations of motion (example)
force = -k * q - m * g
# Create system and simulate
system = System.from_newtonian(force)
results = system.integrate(np.linspace(0, 10, 100))
# Plot results
plt.plot(results[:, 0], results[:, 1])
plt.title('Multibody Dynamics Simulation')
plt.xlabel('Time (s)')
plt.ylabel('Displacement (m)')
plt.show()

