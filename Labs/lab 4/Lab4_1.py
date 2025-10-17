"""
Qube-Servo 3 — State-space simulation with python-control + 5 V step
- Uses control.ss + control.forced_response for the model.
- Sends the same 5 V to the Qube virtual device (if 'pal' is available).
"""

import sys, time
import numpy as np
import matplotlib.pyplot as plt
import control as ct  # python-control

# Try to import the virtual/real device driver
try:
    from pal.products.qube import QubeServo3
    PAL_AVAILABLE = True
except Exception:
    PAL_AVAILABLE = False

# --------- Motor/Load Parameters (adjust as needed) ----------
Rm = 7.5           # Ohm
kt = 0.0422        # N·m/A
km = 0.0422        # V·s/rad
Jm = 1.4e-6
Jh = 0.6e-6
md = 0.053
rd = 0.0248
Jd = 0.5 * md * rd**2
Jeq = Jm + Jh + Jd
b  = 0.0          # small viscous friction (feel free to tune)

# --------- Continuous-time state-space model ----------
# x = [theta, omega]; u = motor voltage (V)
# xdot = A x + B u ; y = C x + D u, with y = [theta, omega]
A = ...
B = ...
C = ...
D = ...

sys = ct.ss(A, B, C, D)

# --------- Simulation settings (5 V step) ----------
V_input = 5.0
T_total = 2.0
dt      = 0.001
t       = np.arange(0.0, T_total + dt, dt)
u       = np.ones_like(t) * V_input

# Option 1: forced_response for arbitrary input (best when not unit-step)
t_sim, y_sim, x_sim = ct.forced_response(sys, T=t, U=u, return_states=True)
theta_sim = ... # first output row is position
omega_sim = ... # first output row is angular velocity

# (FYI: For a unit step you could also do: t_step, y_step = ct.step_response(sys_theta)
# where sys_theta = ct.ss(A, B, C_theta, D_theta) and C_theta = [[1,0]],
# then scale by 5 V. forced_response already handles the 5 V.)

# --------- Virtual lab (same 5 V) ----------
qube_t, qube_theta, qube_omega = [], [], []
if PAL_AVAILABLE:
    try:
        with QubeServo3(hardware=0, pendulum=0) as qube:  # virtual device
            t0 = time.time()
            while True:
                t_now = time.time() - t0
                if t_now >= T_total:
                    break
                qube.read_outputs()
                theta = float(getattr(qube, "MotorPosition",
                                      getattr(qube, "motorPosition")))
                omega = float(getattr(qube, "MotorSpeed",
                                      getattr(qube, "motorSpeed")))
                qube.write_voltage(V_input)
                qube_t.append(t_now)
                qube_theta.append(theta)
                qube_omega.append(omega)
        # be nice: set output to 0 V when done
        try:
            qube.write_voltage(0.0)
        except Exception:
            pass
    except Exception as e:
        print(f"[Qube] skipped due to: {e}", file=sys.stderr)
else:
    print("[Qube] PAL not available — running sim only.", file=sys.stderr)

# --------- Plots ----------
plt.figure(figsize=(9,5))
plt.plot(t_sim, theta_sim, label="SS θ (rad) — control.forced_response")
if qube_t:
    plt.plot(qube_t, qube_theta, label="Qube virtual θ (rad)")
plt.xlabel("Time [s]"); plt.ylabel("θ [rad]")
plt.title("5 V Step Response — Position")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

plt.figure(figsize=(9,5))
plt.plot(t_sim, omega_sim, label="SS ω (rad/s)")
if qube_t:
    plt.plot(qube_t, qube_omega, label="Qube virtual ω (rad/s)")
plt.xlabel("Time [s]"); plt.ylabel("ω [rad/s]")
plt.title("5 V Step Response — Speed")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()
