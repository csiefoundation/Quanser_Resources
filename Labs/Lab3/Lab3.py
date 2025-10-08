"""
Qube-Servo 3 — PD/PID (no filter)  — STUDENT VERSION
Complete the TODOs:
  • Insert your plant (K, tau) from Lab 2, or derive from constants.
  • Implement specs → PD/PID gains (derivative on measurement).
  • Run TF simulation (no saturation) and Qube test.
  • Toggle saturation and explore how lowering OS and tp changes behavior.
"""

import time, sys
import numpy as np
import matplotlib.pyplot as plt
from pal.products.qube import QubeServo3
import control as ct

# ---------------- Plant parameters (Qube-Servo 3) ----------------
Rm   = 7.5
Lm   = 1.15e-3
kt   = 0.0422
km   = 0.0422
Jm   = 1.4e-6
Jh   = 0.6e-6
md   = 0.053
rd   = 0.0248
Jd   = 0.5 * md * rd**2
Jeq  = Jm + Jh + Jd
b    = 0.0  

# ---- Insert your Lab 2 identified plant numbers ----------
Knum    = kt / Rm
alpha_  = b + (kt*km)/Rm
K_PLANT = Knum / alpha_
TAU_PLANT = Jeq / alpha_

print(f"[Plant] K={K_PLANT} rad/s/V, tau={TAU_PLANT} s")

# ---------------- Specs (student sets) ----------------------------
# ---- TODO(1): Choose design specs and explore ↓↓↓
OS = ...     # % overshoot (start ~5–10; then try smaller values)
tp = ...     # peak time [s] (start ~0.15; then try smaller values)

# ---------------- Run settings & reference -----------------------
simulationTime = 10.0
sampleTime     = 0.002  # 500 Hz
amplitude      = 2.0    # rad
period         = np.pi/2  # s

# Saturation toggle:
APPLY_SATURATION = True      # TODO(2): set False for (sim-only) exploration, True for hardware safety
SAFE_VOLTS       = 10.0      # rails [V]; ignored if APPLY_SATURATION=False

def clip_v(v):
    if not APPLY_SATURATION:
        return float(v)
    return float(np.clip(v, -SAFE_VOLTS, SAFE_VOLTS))

def square_waveform(t, amplitude, period):
    return amplitude * np.sign(np.sin(2 * np.pi * t / period))

# ---------------- Specs -> gains (rate-PD and PID) ----------------
def specs_to_pd(K, tau, OS, tp):
    """
    TODO(4): From OS, tp → zeta, wn.
    """
    # zeta = ...
    # wn   = ...
    # kd   = ...
    # kp   = ...
    ki = 0.0
    return kp, ki, kd

k_p, k_i, k_d = specs_to_pd(K_PLANT, TAU_PLANT, OS, tp)

print(f"[Gains] kp={k_p}, ki={k_i}, kd={k_d}  (derivative on measurement)")

# ---------------- (1) TF simulation (matches hardware law) -------
s = ct.TransferFunction.s
P = ...  # TODO: voltage -> position

# Controller structure (NO filter): C_PI forward; D_m = kd*s on measurement path
C_PI = ... #TODO 
D_m  = ... #TODO

# Closed-loop: Y/R = P*C_PI / (1 + P*(C_PI + D_m))
T  = ... #TODO

# Reference and response
t = np.arange(0, simulationTime + sampleTime, sampleTime)
r = np.array([square_waveform(tt, amplitude, period) for tt in t])

# forced_response returns (T, y, x)
t_tf, theta_tf = ct.forced_response(T, T=t, U=r)

# ---------------- (2) Qube loop (virtual by default) -------------
qube_t, qube_v = [], []
qube_theta, qube_omega, qube_theta_des = [], [], []

try:
    with QubeServo3(hardware=0, pendulum=0) as qube:  # set hardware=1 for real device
        I = 0.0
        t0 = time.time()

        while True:
            t_now = time.time() - t0
            if t_now >= simulationTime:
                break

            qube.read_outputs()
            theta = float(getattr(qube, "MotorPosition", getattr(qube, "motorPosition")))
            omega = float(getattr(qube, "MotorSpeed",    getattr(qube, "motorSpeed")))
            theta_des = square_waveform(t_now, amplitude, period)

            e = ... #TODO
            u_unsat = ... # TODO
            v_cmd   = clip_v(u_unsat)

            I += ...   # TODO

            qube.write_voltage(v_cmd)

            qube_t.append(t_now); qube_v.append(v_cmd)
            qube_theta.append(theta); qube_omega.append(omega)
            qube_theta_des.append(theta_des)

            time.sleep(sampleTime)

    HAVE_QUBE = True
except Exception as e:
    HAVE_QUBE = False
    print(f"[Qube] Skipping simulator/hardware due to error: {e}", file=sys.stderr)

# ---------------- Plots ------------------------------------------
plt.figure(figsize=(8,5))
plt.plot(t_tf, theta_tf, label="TF (closed loop)")
plt.plot(t,    r,        "--", label="reference r(t)")
plt.xlabel("time (s)"); plt.ylabel("theta (rad)")
plt.title("Closed-loop position — TF (no filter, deriv on measurement)")
plt.grid(True); plt.legend(); plt.tight_layout()
plt.show()

if 'HAVE_QUBE' in globals() and HAVE_QUBE and len(qube_t) > 0:
    plt.figure(figsize=(8,5))
    th_tf_interp = np.interp(qube_t, t_tf, theta_tf)
    plt.plot(qube_t, qube_theta, label="Qube θ (rad)")
    plt.plot(qube_t, th_tf_interp, "--", label="TF θ (interp)")
    plt.plot(qube_t, qube_theta_des, ":", label="reference")
    plt.xlabel("time (s)"); plt.ylabel("theta (rad)")
    plt.title("Qube vs TF — position")
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8,5))
    plt.plot(qube_t, qube_omega, label="ω (rad/s)")
    plt.xlabel("time (s)"); plt.ylabel("rad/s")
    plt.title("Measured motor speed")
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.show()

    plt.figure(figsize=(8,5))
    plt.plot(qube_t, qube_v, label="u(t) [V]")
    plt.xlabel("time (s)"); plt.ylabel("V")
    sat_txt = "no saturation" if not APPLY_SATURATION else f"clipped at ±{SAFE_VOLTS:g} V"
    plt.title(f"Applied voltage ({sat_txt})")
    plt.grid(True); plt.legend(); plt.tight_layout()
    plt.show()
else:
    print("[Qube] No device data to plot.")
