import time, numpy as np, matplotlib.pyplot as plt
from pal.products.qube import QubeServo3

# TODO-1: set safe voltage limit (suggestion: 3.0 V)
SAFE_VOLTS = ...

def clip_v(v):
    # TODO-2: clip v between -SAFE_VOLTS and +SAFE_VOLTS
    return ...

# Logging arrays
t_log, v_log, counts_log = [], [], []

# TODO-3: open Qube in simulator mode (hardware=?, pendulum=?)
with QubeServo3(hardware=..., pendulum=...) as qube:
    # TODO-4: set run duration (suggestion: 6 s)
    duration = ...
    t0 = time.time()

    # --- Phase 1: Apply +V for ~3 seconds ---
    # TODO-5: choose a positive voltage (0.5-1.5 V)
    V_POS = ...
    while time.time() - t0 < 3.0:
        qube.read_outputs()
        v_cmd = clip_v(V_POS)
        # TODO-6: send the command voltage
        ...

        # Log
        t_now = time.time() - t0
        t_log.append(t_now)
        v_log.append(v_cmd)
        counts_log.append(int(qube.motorEncoderCounts))

        time.sleep(0.002)

    # --- Phase 2: Apply -V for ~3 seconds ---
    # TODO-7: apply the same magnitude but negative
    V_NEG = ...
    t1 = time.time()
    while time.time() - t1 < 3.0:
        qube.read_outputs()
        v_cmd = clip_v(V_NEG)
        # TODO-8: send the command voltage
        ...

        t_now = time.time() - t0
        t_log.append(t_now)
        v_log.append(v_cmd)
        counts_log.append(int(qube.motorEncoderCounts))

        time.sleep(0.002)

# Plot command and counts
plt.figure(figsize=(9,6))
plt.subplot(2,1,1)
plt.plot(t_log, v_log, label="command voltage (V)")
plt.ylabel("V"); plt.grid(True); plt.legend()

plt.subplot(2,1,2)
plt.plot(t_log, counts_log, label="motor encoder counts")
plt.xlabel("time (s)"); plt.ylabel("counts"); plt.grid(True); plt.legend()

plt.tight_layout(); plt.show()

# TODO-9 (report): Which direction did the disc rotate each time?
# TODO-10 (report): What changes in the plots when you reduce the voltage?
