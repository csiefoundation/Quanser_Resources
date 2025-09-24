import time, numpy as np, matplotlib.pyplot as plt
from pal.products.qube import QubeServo3

# TODO-1: compute RAD_PER_COUNT again
RAD_PER_COUNT = ...

SAFE_VOLTS = ...
def clip_v(v): return ...

t_log, v_log, counts_log = [], [], []

# TODO-2: switch to hardware=1
with QubeServo3(hardware=..., pendulum=0) as qube:
    # TODO-3: choose a small step voltage (<= 0.5 V)
    STEP = ...
    HOLD = 2.0
    RUN_T = 5.0

    qube.read_outputs()
    # TODO-4: record initial counts
    N0 = ...

    t0 = time.time()
    while time.time() - t0 < RUN_T:
        qube.read_outputs()
        t = time.time() - t0

        # --- Command logic ---
        # TODO-5: apply STEP for first HOLD seconds, then 0
        v_cmd = ...
        v_cmd = clip_v(v_cmd)
        # TODO-6: send the command voltage
        ...

        # Safety check
        if qube.amplifierFault or qube.motorStallError:
            print("Fault detected! Stopping.")
            # TODO-7: stop the motor safely
            ...
            break

        # Log
        t_log.append(t); v_log.append(v_cmd)
        counts_log.append(int(qube.motorEncoderCounts))

        time.sleep(0.002)

    qube.read_outputs()
    # TODO-8: compute dN and revolutions
    N1 = ...
    dN = ...
    rev_hw = ...
    print("Hardware: dN={}, rev={}".format(dN, rev_hw))

# Plot voltage and counts
plt.figure(figsize=(9,6))
plt.subplot(2,1,1)
plt.plot(t_log, v_log, label="command voltage (V)")
plt.ylabel("V"); plt.grid(True); plt.legend()

plt.subplot(2,1,2)
plt.plot(t_log, counts_log, label="motor encoder counts")
plt.xlabel("time (s)"); plt.ylabel("counts"); plt.grid(True); plt.legend()

plt.tight_layout(); plt.show()