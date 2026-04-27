import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint
# Define equations of motion
def spacecraft_motion(y, t, u):
    pos, vel = y
    dydt = [vel, u]
    return dydt
# Initial conditions
y0 = [0.0, 0.0]
# Time points
t = np.linspace(0, 10, 100)
# Control input (constant force)
u = 1.0
# Solve ODE
sol = odeint(spacecraft_motion, y0, t, args=(u,))
# Plot motion trajectories
plt.plot(t, sol[:, 0], label='Position (m)')
plt.plot(t, sol[:, 1], label='Velocity (m/s)')
plt.xlabel('Time (s)')
plt.ylabel('Response')
plt.legend()
plt.title('Spacecraft Kinematics During Docking')
plt.show()

