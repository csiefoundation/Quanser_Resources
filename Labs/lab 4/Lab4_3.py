## example_pd_control_qube_hardware_task.py
# This example sets up a PD controller to control the position of the QUBE Servo Disk.
# This example uses either a virtual or Physical Qube Servo 2 or Physical Qube Servo 3 device,
# in a task-based (time-based IO) mode where you do not have to handle timing yourself.
# (task based mode is recommended for most applications).
# -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- -- --

# imports
from threading import Thread
import signal
import time
import math
import numpy as np
from pal.products.qube import QubeServo2, QubeServo3
from pal.utilities.math import SignalGenerator
from pal.utilities.scope import Scope
import control as ct

# Setup to enable killing the data generation thread using keyboard interrupts
global KILL_THREAD
KILL_THREAD = False
def sig_handler(*args):
    global KILL_THREAD
    KILL_THREAD = True
signal.signal(signal.SIGINT, sig_handler)


#region: Setup
simulationTime = 30 # will run for 30 seconds
color = np.array([0, 1, 0], dtype=np.float64)

A = np.array([
    [0.0, 0.0, 1.0, 0.0],
    [0.0, 0.0, 0.0, 1.0],
    [0.0, 55.1525, -4.5471, -0.1816],
    [0, 168.6810, -4.492, -0.5551]
])
B = np.array([
    [0.0],
    [0.0],
    [20.6755],
    [20.4351]
])

Q = ...
R = ...

K, S, E = ct.lqr(A, B, Q, R)   # u = -K x

scopePendulum = Scope(
    title='Pendulum encoder - alpha (rad)',
    timeWindow=10,
    xLabel='Time (s)',
    yLabel='Position (rad)')
scopePendulum.attachSignal(name='Pendulum - alpha (rad)',  width=1)

scopeBase = Scope(
    title='Base encoder - theta (rad)',
    timeWindow=10,
    xLabel='Time (s)',
    yLabel='Position (rad)')
scopeBase.attachSignal(name='Base - theta (rad)',  width=1)

scopeVoltage = Scope(
    title='Motor Voltage',
    timeWindow=10,
    xLabel='Time (s)',
    yLabel='Voltage (volts)')
scopeVoltage.attachSignal(name='Voltage',  width=1)

#endregion

# Code to control the Qube Hardware
# CHANGE qubeVersion, hardware and pendulum VARIABLES FOR DIFFERENT SETUPS
def control_loop():
    frequency = 500# Hz

    # Limit sample rate for scope to 50 hz
    countMax = frequency / 50
    count = 0

    with QubeServo3(hardware=0, pendulum=1, frequency=frequency) as myQube:

        startTime = 0
        timeStamp = 0
        def elapsed_time():
            return time.time() - startTime
        startTime = time.time()

        while timeStamp < simulationTime and not KILL_THREAD:

            # Read sensor information
            myQube.read_outputs()

            theta = myQube.motorPosition * -1
            alpha_f =  myQube.pendulumPosition
            alpha = np.mod(alpha_f, 2*np.pi) - np.pi
            alpha_degrees = abs(math.degrees(alpha))
            theta_dot = myQube.motorSpeed
            alpha_dot = myQube.pendulumSpeed

            command_deg = 0

            states = command_deg*np.array([np.pi/180, 0, 0, 0]) - np.array([theta, alpha, theta_dot, alpha_dot])

            if alpha_degrees > 10:
                voltage = 0
            else:
                voltage = ...

            # # Write commands
            myQube.write_voltage(voltage)

            # Plot to scopes
            count += 1
            if count >= countMax:
                scopePendulum.sample(timeStamp, [states[1]])
                scopeBase.sample(timeStamp, [states[0]])
                scopeVoltage.sample(timeStamp,[voltage])
                count = 0

            timeStamp = elapsed_time()



# Setup data generation thread and run until complete
thread = Thread(target=control_loop)
thread.start()

while thread.is_alive() and (not KILL_THREAD):

    # This must be called regularly or the scope windows will freeze
    # Must be called in the main thread.
    Scope.refreshAll()
    time.sleep(0.01)


input('Press the enter key to exit.')
