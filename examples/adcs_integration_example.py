#!/usr/bin/env python3
"""Example: Integrating DDMS with Satellite ADCS Hardware.

This example shows how to:
1. Connect to ADCS flight computer
2. Read sensor telemetry
3. Send attitude commands to execute maneuvers
4. Handle real-time communication
"""

import time
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional


@dataclass
class AttitudeState:
    """Satellite attitude state vector."""
    roll_deg: float       # Rotation around longitudinal axis
    pitch_deg: float      # Rotation around lateral axis
    yaw_deg: float        # Rotation around vertical axis
    roll_rate_deg_s: float
    pitch_rate_deg_s: float
    yaw_rate_deg_s: float
    timestamp_utc: float  # Unix timestamp


@dataclass
class ActuatorCommand:
    """Commanded attitude for ADCS actuators."""
    target_roll_deg: float
    target_pitch_deg: float
    target_yaw_deg: float
    torque_limit_nm: float = 0.1  # Newton-meters
    max_angular_rate_deg_s: float = 5.0
    duration_seconds: float = 60.0


class ADCSInterface(ABC):
    """Abstract base class for ADCS hardware interfaces."""
    
    @abstractmethod
    def connect(self, port: str, baudrate: int = 115200):
        """Connect to ADCS flight computer."""
        pass
    
    @abstractmethod
    def disconnect(self):
        """Close connection to ADCS."""
        pass
    
    @abstractmethod
    def read_telemetry(self) -> AttitudeState:
        """Read current satellite attitude from sensors."""
        pass
    
    @abstractmethod
    def send_command(self, command: ActuatorCommand) -> bool:
        """Send attitude command to ADCS."""
        pass
    
    @abstractmethod
    def is_connected(self) -> bool:
        """Check if connected to ADCS."""
        pass


class SerialADCSInterface(ADCSInterface):
    """Serial-based ADCS interface (RS-485, UART, etc.).
    
    Example: Interfacing with common ADCS boards like:
    - Blue Canyon Technologies (BCT)
    - Hyperion Technologies
    - Argon Design
    """
    
    def __init__(self):
        self.serial_port = None
        self.connected = False
    
    def connect(self, port: str, baudrate: int = 115200):
        """Connect to ADCS via serial port.
        
        Args:
            port: Serial port name (e.g., '/dev/ttyUSB0' or 'COM3')
            baudrate: Serial communication speed (default 115200)
        """
        try:
            import serial
            self.serial_port = serial.Serial(port, baudrate, timeout=1.0)
            self.connected = True
            print(f"[ADCS] Connected to {port} at {baudrate} baud")
        except ImportError:
            print("[ADCS] PySerial not installed. Install with: pip install pyserial")
        except Exception as e:
            print(f"[ADCS] Connection failed: {e}")
            self.connected = False
    
    def disconnect(self):
        """Close serial connection."""
        if self.serial_port:
            self.serial_port.close()
            self.connected = False
            print("[ADCS] Disconnected")
    
    def read_telemetry(self) -> Optional[AttitudeState]:
        """Read attitude telemetry from ADCS.
        
        Expected message format (example):
        $ADCS,roll,pitch,yaw,roll_rate,pitch_rate,yaw_rate,timestamp*checksum
        """
        if not self.is_connected():
            return None
        
        try:
            # Read line from serial
            line = self.serial_port.readline().decode('utf-8').strip()
            
            if line.startswith('$ADCS'):
                parts = line.split(',')
                return AttitudeState(
                    roll_deg=float(parts[1]),
                    pitch_deg=float(parts[2]),
                    yaw_deg=float(parts[3]),
                    roll_rate_deg_s=float(parts[4]),
                    pitch_rate_deg_s=float(parts[5]),
                    yaw_rate_deg_s=float(parts[6]),
                    timestamp_utc=float(parts[7])
                )
        except Exception as e:
            print(f"[ADCS] Telemetry read error: {e}")
        
        return None
    
    def send_command(self, command: ActuatorCommand) -> bool:
        """Send attitude control command to ADCS.
        
        Command format:
        $CMD,roll_target,pitch_target,yaw_target,torque_limit,max_rate,duration*checksum
        """
        if not self.is_connected():
            print("[ADCS] Not connected")
            return False
        
        try:
            # Format command message
            msg = f"$CMD,{command.target_roll_deg},{command.target_pitch_deg},"
            msg += f"{command.target_yaw_deg},{command.torque_limit_nm},"
            msg += f"{command.max_angular_rate_deg_s},{command.duration_seconds}\n"
            
            # Send via serial
            self.serial_port.write(msg.encode('utf-8'))
            print(f"[ADCS] Command sent: roll={command.target_roll_deg}°, "
                  f"pitch={command.target_pitch_deg}°, yaw={command.target_yaw_deg}°")
            
            return True
        except Exception as e:
            print(f"[ADCS] Command send error: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self.connected and self.serial_port is not None


class CANBusADCSInterface(ADCSInterface):
    """CAN-bus based ADCS interface.
    
    For satellites using CAN (Controller Area Network) for ADCS communication.
    """
    
    def __init__(self):
        self.can_bus = None
        self.connected = False
    
    def connect(self, port: str, baudrate: int = 250000):
        """Connect to ADCS via CAN bus.
        
        Args:
            port: CAN device (e.g., 'vcan0' on Linux)
            baudrate: CAN bus speed (typically 250k or 500k)
        """
        try:
            import can
            self.can_bus = can.interface.Bus(channel=port, bustype='socketcan',
                                            bitrate=baudrate)
            self.connected = True
            print(f"[ADCS-CAN] Connected to {port} at {baudrate} baud")
        except ImportError:
            print("[ADCS-CAN] python-can not installed. Install with: pip install python-can")
        except Exception as e:
            print(f"[ADCS-CAN] Connection failed: {e}")
    
    def disconnect(self):
        if self.can_bus:
            self.can_bus.shutdown()
            self.connected = False
            print("[ADCS-CAN] Disconnected")
    
    def read_telemetry(self) -> Optional[AttitudeState]:
        """Read attitude telemetry via CAN."""
        if not self.is_connected():
            return None
        
        try:
            import can
            # Read CAN message with attitude data (CAN ID 0x123)
            msg = self.can_bus.recv(timeout=1.0)
            
            if msg and msg.arbitration_id == 0x123:
                # Parse CAN data (example format)
                # Bytes: [roll, pitch, yaw, roll_rate, pitch_rate, yaw_rate]
                return AttitudeState(
                    roll_deg=msg.data[0],
                    pitch_deg=msg.data[1],
                    yaw_deg=msg.data[2],
                    roll_rate_deg_s=msg.data[3],
                    pitch_rate_deg_s=msg.data[4],
                    yaw_rate_deg_s=msg.data[5],
                    timestamp_utc=time.time()
                )
        except Exception as e:
            print(f"[ADCS-CAN] Telemetry read error: {e}")
        
        return None
    
    def send_command(self, command: ActuatorCommand) -> bool:
        """Send attitude command via CAN."""
        if not self.is_connected():
            return False
        
        try:
            import can
            # Create CAN message (ID 0x456)
            data = [
                int(command.target_roll_deg) & 0xFF,
                int(command.target_pitch_deg) & 0xFF,
                int(command.target_yaw_deg) & 0xFF,
                int(command.torque_limit_nm * 100) & 0xFF,
                int(command.max_angular_rate_deg_s) & 0xFF,
                int(command.duration_seconds) & 0xFF,
            ]
            
            msg = can.Message(arbitration_id=0x456, data=data)
            self.can_bus.send(msg)
            print(f"[ADCS-CAN] Command sent via CAN ID 0x456")
            
            return True
        except Exception as e:
            print(f"[ADCS-CAN] Command send error: {e}")
            return False
    
    def is_connected(self) -> bool:
        return self.connected and self.can_bus is not None


class MockADCSInterface(ADCSInterface):
    """Mock ADCS interface for testing (no hardware required)."""
    
    def __init__(self):
        self.connected = False
        self.current_attitude = AttitudeState(
            roll_deg=0.0, pitch_deg=0.0, yaw_deg=0.0,
            roll_rate_deg_s=0.0, pitch_rate_deg_s=0.0, yaw_rate_deg_s=0.0,
            timestamp_utc=time.time()
        )
    
    def connect(self, port: str = "mock", baudrate: int = 115200):
        self.connected = True
        print(f"[ADCS-MOCK] Mock interface connected")
    
    def disconnect(self):
        self.connected = False
        print("[ADCS-MOCK] Disconnected")
    
    def read_telemetry(self) -> Optional[AttitudeState]:
        if not self.is_connected():
            return None
        return self.current_attitude
    
    def send_command(self, command: ActuatorCommand) -> bool:
        if not self.is_connected():
            return False
        
        # Simulate attitude change
        self.current_attitude.roll_deg = command.target_roll_deg
        self.current_attitude.pitch_deg = command.target_pitch_deg
        self.current_attitude.yaw_deg = command.target_yaw_deg
        
        print(f"[ADCS-MOCK] Simulated command: "
              f"roll={command.target_roll_deg}°, "
              f"pitch={command.target_pitch_deg}°, "
              f"yaw={command.target_yaw_deg}°")
        
        return True
    
    def is_connected(self) -> bool:
        return self.connected


def ddms_control_loop_example():
    """Example DDMS control loop integrated with ADCS."""
    
    print("\n" + "="*70)
    print("DDMS ↔ ADCS Integration Example")
    print("="*70 + "\n")
    
    # Step 1: Initialize ADCS interface
    print("[Step 1] Establish ADCS Connection")
    print("-" * 70)
    
    # Use mock interface for demo (no hardware required)
    adcs = MockADCSInterface()
    adcs.connect()
    
    # In real usage, choose appropriate interface:
    # adcs = SerialADCSInterface()
    # adcs.connect('/dev/ttyUSB0', 115200)
    #
    # OR:
    # adcs = CANBusADCSInterface()
    # adcs.connect('vcan0', 250000)
    
    # Step 2: Main control loop
    print("\n[Step 2] DDMS Control Loop (Simulated)")
    print("-" * 70)
    
    for iteration in range(3):
        print(f"\n--- Iteration {iteration + 1} ---")
        
        # Read current attitude
        attitude = adcs.read_telemetry()
        if attitude:
            print(f"  Current Attitude:")
            print(f"    - Roll:  {attitude.roll_deg:.1f}°")
            print(f"    - Pitch: {attitude.pitch_deg:.1f}°")
            print(f"    - Yaw:   {attitude.yaw_deg:.1f}°")
        
        # Simulate DDMS decision (in real system, this comes from AECRM)
        print(f"  DDMS Risk Assessment: Collision probability = 1.5e-3")
        print(f"  DDMS Decision: MANEUVER REQUIRED (Drag-Up strategy)")
        
        # Send maneuver command
        if iteration == 0:
            # First maneuver: expose surface for drag
            cmd = ActuatorCommand(
                target_roll_deg=45.0,   # Tilt body
                target_pitch_deg=0.0,
                target_yaw_deg=0.0,
                torque_limit_nm=0.1,
                max_angular_rate_deg_s=2.0,
                duration_seconds=300.0  # 5 minutes
            )
        elif iteration == 1:
            # Maintain drag-up posture
            cmd = ActuatorCommand(
                target_roll_deg=45.0,
                target_pitch_deg=0.0,
                target_yaw_deg=0.0,
                duration_seconds=300.0
            )
        else:
            # Return to nominal attitude
            cmd = ActuatorCommand(
                target_roll_deg=0.0,
                target_pitch_deg=0.0,
                target_yaw_deg=0.0,
                duration_seconds=60.0
            )
        
        success = adcs.send_command(cmd)
        print(f"  Command Status: {'✓ Sent' if success else '✗ Failed'}")
        
        time.sleep(1)  # Simulate delay between iterations
    
    # Step 3: Cleanup
    print("\n[Step 3] Maneuver Complete - Return to Nominal")
    print("-" * 70)
    adcs.disconnect()
    print("  ✓ ADCS connection closed")
    print("  ✓ Collision risk mitigated")
    print("  ✓ Satellite safe\n")


if __name__ == "__main__":
    ddms_control_loop_example()
