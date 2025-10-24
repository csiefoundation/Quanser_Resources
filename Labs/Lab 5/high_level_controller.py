"""
Lab 5 - High-Level Motion Control (Student Version with REQUIRED TODOs)
-----------------------------------------------------------------------
Your tasks:
  • Choose the correct URI (sim OR hardware)
  • Set a sensible default hover height
  • Configure background logging variables
  • Implement basic motion primitives (forward/left/right/back)
  • (Bonus) Implement/open an open-loop square
  • Save logs and produce plots

HINTS:
  - Simulator (CrazySim): URI = "udp://0.0.0.0:19850"
  - Hardware: URI = f"radio://0/<group>/2M"  (replace <group>)
"""

import time
import logging
import threading
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.motion_commander import MotionCommander


# ================================================================
# 0) REQUIRED TODOs (change these!)
# ================================================================

# TODO (REQUIRED): pick ONE. Set to a float in meters, e.g., 0.4–0.6
DEFAULT_HEIGHT = ...  # e.g., 0.5

# TODO (REQUIRED): choose exactly ONE URI (sim or hardware)
URI = ...


logging.basicConfig(level=logging.ERROR)
print("Initializing Crazyflie drivers...")
cflib.crtp.init_drivers(enable_debug_driver=False)


# ================================================================
# 1) (Optional) Estimator reset helper — enable if needed
# ================================================================
def reset_estimator(cf):
    """
    OPTIONAL (but recommended between flights on hardware):
    Reset the onboard Kalman filter to clear position drift.
    Uncomment the call sites if you want to use it.
    """
    cf.param.set_value("kalman.resetEstimation", "1")
    time.sleep(0.1)
    cf.param.set_value("kalman.resetEstimation", "0")
    time.sleep(1.0)


# ================================================================
# 2) Background logger
# ================================================================
class CFLogger:
    """
    Background logger that samples attitude + position into arrays.
    """
    def __init__(self, scf, period_ms=50):
        self.scf = scf
        self.running = False
        self.data = {"t": [], "roll": [], "pitch": [], "yaw": [], "x": [], "y": [], "z": []}
        self._start_time = None
        self._thread = None

        self.logconf = LogConfig(name="State", period_in_ms=period_ms)
        self.logconf.add_variable("stabilizer.roll", "float")
        self.logconf.add_variable("stabilizer.pitch", "float")
        self.logconf.add_variable("stabilizer.yaw", "float")
        self.logconf.add_variable("stateEstimate.x", "float")
        self.logconf.add_variable("stateEstimate.y", "float")
        self.logconf.add_variable("stateEstimate.z", "float")

        # Flip this to True once you have added all variables
        self._added_vars = False  # ← set to True when done

    def _loop(self):
        if not self._added_vars:
            raise NotImplementedError(
                "Add log variables in CFLogger.__init__ and set self._added_vars = True."
            )

        self._start_time = time.time()
        try:
            with SyncLogger(self.scf, self.logconf) as logger:
                for ts, data, _name in logger:
                    if not self.running:
                        break
                    t = time.time() - self._start_time
                    
                    r = float(data["stabilizer.roll"])
                    p = float(data["stabilizer.pitch"])
                    yw = float(data["stabilizer.yaw"])
                    x = float(data["stateEstimate.x"])
                    y = float(data["stateEstimate.y"])
                    z = float(data["stateEstimate.z"])

                    self.data["t"].append(t)
                    self.data["roll"].append(r)
                    self.data["pitch"].append(p)
                    self.data["yaw"].append(yw)
                    self.data["x"].append(x)
                    self.data["y"].append(y)
                    self.data["z"].append(z)

                    raise NotImplementedError(
                        "Fill the logger loop: extract variables from 'data' and append to self.data."
                    )
        except Exception as e:
            print(f"[Logger] Stopped with exception: {e}")

    def start(self):
        if self.running:
            return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running:
            return
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)


# ================================================================
# 3) Flight steps 
# ================================================================
def simple_takeoff_land(scf):
    """
    Step 1: Takeoff → short hover → land
    MotionCommander auto-takes off on entry to its context.
    """
    print("\n[Step 1] Takeoff test...")
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        # TODO (OPTIONAL): adjust hover duration
        time.sleep(3.0)
        mc.land()
        print("Landing complete.")


def basic_moves(scf):
    """
    Step 2: Implement basic directional moves.
    REQUIREMENTS:
      - forward(0.2), left(0.2), right(0.2), back(0.2)
      - ~1.0 s pause between each
    """
    print("\n[Step 2] Basic directional moves...")
    with MotionCommander(scf, default_height=DEFAULT_HEIGHT) as mc:
        # TODO (REQUIRED): implement these 4 moves with ~1.0 s sleeps between:


        raise NotImplementedError(
            "Implement Step 2 basic moves (forward/left/right/back) with pauses."
        )

        # TODO (REQUIRED): Land after finishing
        print("Landing complete.")


# ================================================================
# 4) Plotting
# ================================================================
def make_plots(data):
    """Make 2D attitude/position plots and a 3D trajectory."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        # Sanity check
        if len(data["t"]) == 0:
            raise RuntimeError(
                "No samples in logger data. Complete the logging TODOs first."
            )

        t = np.array(data["t"])
        roll = np.array(data["roll"])
        pitch = np.array(data["pitch"])
        yaw = np.array(data["yaw"])
        x = np.array(data["x"])
        y = np.array(data["y"])
        z = np.array(data["z"])

        # 2D: Attitude / Position
        fig, axs = plt.subplots(2, 1, figsize=(12, 8))
        axs[0].plot(t, roll, label="Roll")
        axs[0].plot(t, pitch, label="Pitch")
        axs[0].plot(t, yaw, label="Yaw")
        axs[0].set_title("Attitude vs Time")
        axs[0].set_xlabel("Time [s]")
        axs[0].set_ylabel("Angle [deg]")
        axs[0].legend()
        axs[0].grid(True)

        axs[1].plot(t, x, label="X")
        axs[1].plot(t, y, label="Y")
        axs[1].plot(t, z, label="Z")
        axs[1].set_title("Position vs Time")
        axs[1].set_xlabel("Time [s]")
        axs[1].set_ylabel("Position [m]")
        axs[1].legend()
        axs[1].grid(True)

        plt.tight_layout()
        plt.show()

        # 3D trajectory
        fig3d = plt.figure(figsize=(7, 6))
        ax3d = fig3d.add_subplot(111, projection="3d")
        ax3d.plot(x, y, z, linewidth=2, label="Trajectory")
        ax3d.scatter(x[0], y[0], z[0], s=40, label="Start")
        ax3d.scatter(x[-1], y[-1], z[-1], s=40, label="End")
        ax3d.set_xlabel("X [m]")
        ax3d.set_ylabel("Y [m]")
        ax3d.set_zlabel("Z [m]")
        ax3d.set_title("3D Trajectory")
        ax3d.legend()
        ax3d.grid(True)
        ax3d.view_init(elev=25, azim=-60)
        plt.tight_layout()
        plt.show()

    except ImportError:
        print("matplotlib not installed — skipping plots.")


# ================================================================
# 5) MAIN 
# ================================================================
if __name__ == "__main__":
    print(f"Connecting to {URI} ...")
    try:
        with SyncCrazyflie(URI, cf=Crazyflie(rw_cache="./cache")) as scf:
            cf = scf.cf
            print("Connected successfully!")

            # OPTIONAL: reset estimator between flights on hardware
            # reset_estimator(cf)

            # Start background logger
            logger = CFLogger(scf, period_ms=50)
            logger.start()
            time.sleep(0.2)  # warm-up for logger

            # --- Flights ---
            simple_takeoff_land(scf)
            time.sleep(1.0)

            basic_moves(scf)          
            time.sleep(1.0)

            # Stop logging and persist data
            logger.stop()
            import os
            os.makedirs("quad_data", exist_ok=True)

            # TODO (REQUIRED): choose a filename for your saved log (e.g., 'hl_demo_log.npz')
            save_path = "quad_data/CHANGE_ME_filename.npz"
            if "CHANGE_ME" in save_path:
                raise NotImplementedError(
                    "Pick a save filename (set 'save_path' without CHANGE_ME)."
                )

            np.savez(save_path, **logger.data)
            print(f"Saved log to {save_path}")

            # Make plots
            make_plots(logger.data)

    except Exception as e:
        print(f"Error during operation: {e}")

    finally:
        print("\n✅ Lab 1 high-level control (student TODO version) complete.")
