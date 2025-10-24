"""
Lab 5 - Crazyflie Logging Exercise (Student Version)
----------------------------------------------------
In this lab, you will:
  • Connect to a Crazyflie
  • Log roll, pitch, yaw (attitude)
  • Log x, y, z (Loco position estimates)
  • Visualize data in 2D and 3D

Fill in all TODO sections and test both in simulation (CrazySim)
and on your actual Crazyflie hardware.
"""

import time
import logging
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger


# ---------------------------------------------------------------------
# 1. SETUP
# ---------------------------------------------------------------------

# TODO: Construct your URI (replace with your group channel)
URI = ...

# Initialize drivers
logging.basicConfig(level=logging.ERROR)
print("Initializing Crazyflie drivers...")
cflib.crtp.init_drivers(enable_debug_driver=False)


# ---------------------------------------------------------------------
# 2. LOGGING CONFIGURATION
# ---------------------------------------------------------------------

# TODO: Create a LogConfig object (name it "StateEstimate", 100 ms period)
lg_stab = LogConfig(name="TODO", period_in_ms=100)

# TODO: Add variables for roll, pitch, yaw
# Example:
# lg_stab.add_variable("stabilizer.roll", "float")

# TODO: Add variables for Loco position (x, y, z)
# Example:
# lg_stab.add_variable("stateEstimate.x", "float")

# ---------------------------------------------------------------------
# 3. CONNECT AND LOG DATA
# ---------------------------------------------------------------------

print(f"Connecting to Crazyflie on {URI}...")
data_log = {
    "time": [],
    "roll": [], "pitch": [], "yaw": [],
    "x": [], "y": [], "z": []
}

try:
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache")) as scf:
        print("Connected successfully!")

        cf = scf.cf

        # TODO: Reset the Kalman filter before logging
        # Hint: use cf.param.set_value("kalman.resetEstimation", "1")
        # Wait briefly, then set it back to "0"
        # (This ensures the position estimates start from a clean state.)

        # TODO: Start logging using SyncLogger
        with SyncLogger(scf, lg_stab) as logger:
            start_time = time.time()
            print("Logging data for 10 seconds...")

            for log_entry in logger:
                timestamp = log_entry[0]
                data = log_entry[1]

                # TODO: Read roll, pitch, yaw, x, y, z from the 'data' dictionary
                # Example: roll = data["stabilizer.roll"]

                # TODO: Append each variable to data_log

                elapsed = time.time() - start_time

                # Print progress roughly once per second
                if int(elapsed * 10) % 10 == 0:
                    print(f"[t={elapsed:5.2f}s] Logging...")

                # Stop after ~10 seconds
                if elapsed > 10:
                    break

except Exception as e:
    print(f"Error: {e}")

finally:
    print("Logging complete.")
    print(f"Saved {len(data_log['time'])} samples.")


# ---------------------------------------------------------------------
# 4. SAVE RESULTS
# ---------------------------------------------------------------------

# TODO: Save the data as a compressed NumPy file (.npz)
# Example:
# np.savez("crazyflie_log_data.npz", **data_log)

print("Data saved! You can now visualize your logs.")


# ---------------------------------------------------------------------
# 5. VISUALIZATION (2D and 3D)
# ---------------------------------------------------------------------

try:
    import matplotlib.pyplot as plt
    from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

    # --- 2D Attitude ---
    fig = plt.figure(figsize=(12, 10))
    ax1 = fig.add_subplot(2, 1, 1)

    # TODO: Plot roll, pitch, yaw vs. time
    # ax1.plot(data_log["time"], data_log["roll"], label="Roll")

    ax1.set_title("Crazyflie Attitude")
    ax1.set_xlabel("Time [s]")
    ax1.set_ylabel("Angle [deg]")
    ax1.legend()
    ax1.grid(True)

    # --- 2D Position ---
    ax2 = fig.add_subplot(2, 1, 2)
    # TODO: Plot x, y, z vs. time
    # ax2.plot(data_log["time"], data_log["x"], label="X")

    ax2.set_title("Loco Position Estimate")
    ax2.set_xlabel("Time [s]")
    ax2.set_ylabel("Position [m]")
    ax2.legend()
    ax2.grid(True)

    plt.tight_layout()
    plt.show()

    # --- 3D Trajectory ---
    fig3d = plt.figure(figsize=(8, 6))
    ax3d = fig3d.add_subplot(111, projection='3d')

    # TODO: Plot the 3D path (x, y, z)
    # ax3d.plot(data_log["x"], data_log["y"], data_log["z"], color="blue", linewidth=2)

    # Mark start and end points
    # ax3d.scatter(data_log["x"][0], data_log["y"][0], data_log["z"][0],
    #              color="green", s=50, label="Start")
    # ax3d.scatter(data_log["x"][-1], data_log["y"][-1], data_log["z"][-1],
    #              color="red", s=50, label="End")

    ax3d.set_xlabel("X [m]")
    ax3d.set_ylabel("Y [m]")
    ax3d.set_zlabel("Z [m]")
    ax3d.set_title("Crazyflie 3D Trajectory (Loco Positioning)")
    ax3d.legend()
    ax3d.grid(True)
    ax3d.view_init(elev=25, azim=-60)

    plt.tight_layout()
    plt.show()

except ImportError:
    print("matplotlib not installed — skipping plots.")
