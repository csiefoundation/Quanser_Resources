# -*- coding: utf-8 -*-
#
# Lab 5 - Closed-Loop Position Control (Student TODO Version) + LOGGING & PLOTS
# Based on Bitcraze's PositionHlCommander example.
=
# Safety: Fly in a net, keep heights small (≤ 0.7 m), and clear the area.

import time
import logging
import threading
import numpy as np

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.utils import uri_helper


# -----------------------------
# 0) REQUIRED CONFIG (set this)
# -----------------------------
# TODO (REQUIRED): Choose the URI
URI = None

if URI is None:
    raise NotImplementedError("Set the URI at the top (sim OR hardware) before running.")

logging.basicConfig(level=logging.ERROR)
cflib.crtp.init_drivers(enable_debug_driver=False)
print(f"Initialized Crazyflie drivers. URI={URI}")


# ----------------------------------------------------------
# (Optional) Estimator reset helper — useful on hardware
# ----------------------------------------------------------
def reset_estimator(cf):
    cf.param.set_value("kalman.resetEstimation", "1")
    time.sleep(0.1)
    cf.param.set_value("kalman.resetEstimation", "0")
    time.sleep(1.0)


# ----------------------------------------------------------
# Background logger (students do not need to edit)
# ----------------------------------------------------------
class CFLogger:
    """Background logger: attitude + position at ~20 Hz (period_ms=50)."""
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

    def _loop(self):
        self._start_time = time.time()
        try:
            with SyncLogger(self.scf, self.logconf) as logger:
                for ts, data, _ in logger:
                    if not self.running:
                        break
                    t = time.time() - self._start_time
                    self.data["t"].append(t)
                    self.data["roll"].append(float(data["stabilizer.roll"]))
                    self.data["pitch"].append(float(data["stabilizer.pitch"]))
                    self.data["yaw"].append(float(data["stabilizer.yaw"]))
                    self.data["x"].append(float(data["stateEstimate.x"]))
                    self.data["y"].append(float(data["stateEstimate.y"]))
                    self.data["z"].append(float(data["stateEstimate.z"]))
        except Exception as e:
            print(f"[Logger] Exception: {e}")

    def start(self):
        if self.running: return
        self.running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)
        self._thread.start()

    def stop(self):
        if not self.running: return
        self.running = False
        if self._thread:
            self._thread.join(timeout=2.0)


# ----------------------------------------------------------
# Plotting helper (provided)
# ----------------------------------------------------------
def make_plots(data):
    """Plot attitude/position vs time and a 3D trajectory."""
    try:
        import matplotlib.pyplot as plt
        from mpl_toolkits.mplot3d import Axes3D  # noqa: F401

        if len(data["t"]) == 0:
            raise RuntimeError("No samples logged. Did you run a flight?")

        t = np.array(data["t"])
        roll = np.array(data["roll"]); pitch = np.array(data["pitch"]); yaw = np.array(data["yaw"])
        x = np.array(data["x"]); y = np.array(data["y"]); z = np.array(data["z"])

        # 2× time plots
        fig, axs = plt.subplots(2, 1, figsize=(12, 8))
        axs[0].plot(t, roll, label="Roll"); axs[0].plot(t, pitch, label="Pitch"); axs[0].plot(t, yaw, label="Yaw")
        axs[0].set_title("Attitude vs Time"); axs[0].set_xlabel("Time [s]"); axs[0].set_ylabel("Angle [deg]")
        axs[0].legend(); axs[0].grid(True)

        axs[1].plot(t, x, label="X"); axs[1].plot(t, y, label="Y"); axs[1].plot(t, z, label="Z")
        axs[1].set_title("Position vs Time"); axs[1].set_xlabel("Time [s]"); axs[1].set_ylabel("Position [m]")
        axs[1].legend(); axs[1].grid(True)
        plt.tight_layout(); plt.show()

        # 3D trajectory
        fig3d = plt.figure(figsize=(7, 6))
        ax3d = fig3d.add_subplot(111, projection="3d")
        ax3d.plot(x, y, z, linewidth=2, label="Trajectory")
        ax3d.scatter(x[0], y[0], z[0], s=40, label="Start")
        ax3d.scatter(x[-1], y[-1], z[-1], s=40, label="End")
        ax3d.set_xlabel("X [m]"); ax3d.set_ylabel("Y [m]"); ax3d.set_zlabel("Z [m]")
        ax3d.set_title("3D Trajectory"); ax3d.legend(); ax3d.grid(True)
        ax3d.view_init(elev=25, azim=-60)
        plt.tight_layout(); plt.show()

    except ImportError:
        print("matplotlib not installed — skipping plots.")


# ----------------------------------------------------------
# 1) REQUIRED: simple closed-loop sequence
# ----------------------------------------------------------
def simple_sequence():
    """
    REQUIRED:
      - Use PositionHlCommander with default PID controller
      - Fly forward(1.0), left(1.0), back(1.0)
      - Then go_to(0.0, 0.0, 0.5) to return to a safe point
    """
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Optional (hardware): reset_estimator(scf.cf)
        logger = CFLogger(scf); logger.start(); time.sleep(0.2)

        with PositionHlCommander(scf,
                                 controller=PositionHlCommander.CONTROLLER_PID,
                                 default_height=0.5,
                                 default_velocity=0.3) as pc:
            # TODO: implement the sequence above
            
            raise NotImplementedError("Implement simple_sequence(): forward, left, back, then go_to a safe point.")

        # stop log + save + plot
        logger.stop()
        import os; os.makedirs("quad_data", exist_ok=True)
        save_path = "quad_data/CHANGE_ME_lab5_poshl_simple.npz"  # TODO (REQUIRED)
        if "CHANGE_ME" in save_path:
            raise NotImplementedError("Pick a save filename for your simple_sequence log.")
        np.savez(save_path, **logger.data)
        print(f"[Saved] {save_path}")
        make_plots(logger.data)


# ----------------------------------------------------------
# 2) REQUIRED: slightly more complex usage
# ----------------------------------------------------------
def slightly_more_complex_usage():
    """
    REQUIRED:
      - start at (x=0,y=0,z=0), default_height~0.5, default_velocity~0.3
      - go_to(1.0, 1.0, 1.0)
      - right(1.0)
      - go_to(0.0, 0.0)   (uses default height)
      - go_to(1.0, 1.0, velocity=0.2)
      - set_default_velocity(0.3), set_default_height(1.0), go_to(0.0, 0.0)
    """
    with SyncCrazyflie(URI, cf=Crazyflie(rw_cache='./cache')) as scf:
        # Optional (hardware): reset_estimator(scf.cf)
        logger = CFLogger(scf); logger.start(); time.sleep(0.2)

        with PositionHlCommander(
            scf,
            x=0.0, y=0.0, z=0.0,
            default_velocity=0.3,
            default_height=0.5,
            controller=PositionHlCommander.CONTROLLER_PID
        ) as pc:
            # TODO: implement each step per spec above
            
            raise NotImplementedError("Complete slightly_more_complex_usage() per the checklist in the docstring.")

        # stop log + save + plot
        logger.stop()
        import os; os.makedirs("quad_data", exist_ok=True)
        save_path = "quad_data/CHANGE_ME_lab5_poshl_complex.npz"  # TODO (REQUIRED)
        if "CHANGE_ME" in save_path:
            raise NotImplementedError("Pick a save filename for your complex log.")
        np.savez(save_path, **logger.data)
        print(f"[Saved] {save_path}")
        make_plots(logger.data)


# --------------------------
# 3) Main entry point
# --------------------------
if __name__ == '__main__':
    # Choose ONE to run at a time while testing:
    simple_sequence()
    # slightly_more_complex_usage()
