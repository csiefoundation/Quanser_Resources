import time, csv, numpy as np, matplotlib.pyplot as plt
from pal.products.qube import QubeServo3

# TODO-1: derive rad/count
RAD_PER_COUNT = ...

SAFE_VOLTS = ...
def clip_v(v): return ...

t_log, v_log, counts_log, theta_log = [], [], [], []

# TODO-2: open simulator Qube (servo mode)
with QubeServo3(hardware=..., pendulum=...) as qube:
    # TODO-3: choose pulse amplitude (0.2-1.0 V)
    AMP = ...
    PULSE_LEN = 2.0
    DURATION = 5.0

    t0 = time.time()

    # --- Starting counts at t approx 0 ---
    qube.read_outputs()
    # TODO-4: record starting counts
    N_start = ...

    while True:
        t = time.time() - t0
        if t >= DURATION: break

        qube.read_outputs()
        counts = ...
        theta  = ...   # TODO-5: convert counts to radians

        # --- Apply 2 s pulse then stop ---
        # TODO-6: if t < 2, send AMP volts; else 0 V
        v_cmd = ...
        v_cmd = clip_v(v_cmd)
        # TODO-7: send the command voltage
        ...

        # Log
        t_log.append(t); v_log.append(v_cmd)
        counts_log.append(counts); theta_log.append(theta)

        time.sleep(0.002)

    # --- Ending counts after pulse ---
    qube.read_outputs()
    # TODO-8: record ending counts
    N_end = ...

# --- Post-process ---
# TODO-9: compute dN and revolutions
delta_counts = ...
revolutions = ...

print("N_start={}, N_end={}, dN={}, rev={}".format(N_start, N_end, delta_counts, revolutions))

# Save CSV (optional for report)
with open("lab1_encoder_log.csv","w",newline="") as f:
    csv.writer(f).writerows([("t","v_cmd","counts","theta_rad")]+list(zip(t_log,v_log,counts_log,theta_log)))

# Plot voltage, counts, and angle
plt.figure(figsize=(10,8))

plt.subplot(3,1,1)
plt.plot(t_log, v_log, label="command voltage (V)")
plt.ylabel("V"); plt.grid(True); plt.legend()

plt.subplot(3,1,2)
plt.plot(t_log, counts_log, label="motor encoder counts")
plt.ylabel("counts"); plt.grid(True); plt.legend()

plt.subplot(3,1,3)
plt.plot(t_log, theta_log, label="motor angle (rad)")
plt.xlabel("time (s)"); plt.ylabel("rad"); plt.grid(True); plt.legend()

plt.tight_layout(); plt.show()
