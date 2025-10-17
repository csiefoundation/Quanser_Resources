"""
Task B — Linear Rotary Pendulum (Downward) : τ-input and v-input models
State: x = [theta, alpha, theta_dot, alpha_dot]^T
Models: small-angle linearization about alpha = 0 (downward)
"""

import numpy as np
import matplotlib.pyplot as plt
import time, sys
import control as ct


try:
    from pal.products.qube import QubeServo3
    PAL_AVAILABLE = True
except Exception:
    PAL_AVAILABLE = False

def square_waveform(t, amplitude, period):
    return amplitude * np.sign(np.sin(2 * np.pi * t / period))

# ------------------ Physical parameters (edit as needed) ------------------
mp = 0.024      # pendulum mass [kg]
Lp = 0.129      # pendulum length [m]
l  = Lp / 2.0   # center of mass [m]
mr = 0.095      # rotary arm mass [kg]
r  = 0.085      # rotary arm length [m]
Jr = (1/3)*mr*(r**2)       # rotary arm inertia [kg·m²]
Jp = (1/3)*mp*(Lp**2)      # pendulum inertia [kg·m²]
br = 2.0e-3     # rotary arm viscous damping [N·m·s/rad]
bp = 5.0e-4     # pendulum viscous damping [N·m·s/rad]
g  = 9.81       # gravity [m/s²]

# Motor/electrics (for voltage-input model)
Rm = 7.5        # Ohm
km = 0.0422     # V·s/rad
kt = 0.0422     # N·m/A

# ------------------ Common derived quantity ------------------
Jt = ...    # determinant of mass matrix

# ------------------ (1) Linearized A,B for torque input u = τ ------------------
A_tau = np.array([
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0],
    [0.0, 0.0, 0.0, 0.0]
], dtype=float)

B_tau = np.array([
    [0.0],
    [0.0],
    [0.0],
    [0.0]
], dtype=float)

C = np.array([[0,0,0,0],   
              [0,0,0,0]], dtype=float)
D_tau = np.zeros((2,1))

sys_tau = ct.ss(A_tau, B_tau, C, D_tau)

# ------------------ (2) Convert to voltage input u = v_m ------------------
# tau = (kt/Rm) * v_m  -  (km*kt/Rm) * theta_dot
B_v = ...
A_v = ...

D_v = np.zeros((2,1))
sys_v = ct.ss(A_v, B_v, C, D_v)

# ------------------ Simulate both ------------------
T_final = 10.0
dt = 0.002
t = np.arange(0.0, T_final+dt, dt)

amplitude      = 1.0    # rad
period         = 1.0  # s
u = np.array([square_waveform(tt, amplitude, period) for tt in t])


t_sim, y_sim, x_sim  = ct.forced_response(sys_v,   T=t, U=u,   return_states=True)
theta_sim = y_sim[0, :]
alpha_sim = y_sim[1, :]

# -------------------- Plots --------------------
plt.figure(figsize=(9,5))
plt.plot(t, u, label="input v_m(t) [V]")
plt.title("Input")
plt.xlabel("Time [s]"); plt.ylabel("Voltage [V]")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))
plt.plot(t_sim, theta_sim, label="SS θ (rad)")
plt.title("Rotary Pendulum — Base angle θ")
plt.xlabel("Time [s]"); plt.ylabel("θ [rad]")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))
plt.plot(t_sim, alpha_sim, label="SS α (rad)")
plt.title("Rotary Pendulum — Pendulum angle α")
plt.xlabel("Time [s]"); plt.ylabel("α [rad]")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

