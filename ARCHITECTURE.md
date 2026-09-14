# 🏗️ DDMS Architecture - Deep Technical Dive

## Overview

The Differential Drag Maneuvering System (DDMS) is a three-tier autonomous collision avoidance architecture designed to operate on existing satellite ADCS hardware with zero additional cost or complexity.

---

## Three Core Components

### 1️⃣ Differential Drag Maneuvering Engine (DDME)

**Purpose:** Convert ADCS attitude commands into collision-avoidance orbital maneuvers

#### Physics Foundation
- **Orbital Drag Model:** Uses MSISE-90/00 atmospheric density model
- **Cross-Sectional Area Dynamics:** Real-time computation of effective drag surface
- **Kepler Element Propagation:** SGP4 orbit prediction with J2 perturbations
- **Non-Impulsive Maneuvers:** Continuous low-force orbital alterations

#### Key Algorithms
```
1. Attitude Command → Solar panel angle/satellite orientation
2. Drag Coefficient = f(altitude, cross-section, surface properties)
3. Drag Force = 0.5 * ρ * v² * Cd * A
4. Acceleration = Drag Force / satellite_mass
5. Orbital Element Decay = ∫(acceleration × time)
```

#### Maneuver Types
- **Drag-Up Maneuver:** Increase drag → decay orbit faster → pass under threat
- **Drag-Down Maneuver:** Minimize drag → coast higher → let threat pass below
- **Protective Postures:** Solar panels edge-on → reduce micrometeoroid impact
- **RF Power Cycling:** Turn off sensitive receivers during debris showers

#### Performance Characteristics
- Achieves ±100m altitude change per orbit (LEO 400km)
- Sustained maneuver duration: 3-24 hours
- Energy cost: Attitude control only (no propellant)
- Graceful degradation if ADCS unavailable

---

### 2️⃣ Autonomous Edge-Computed Risk Matrix (AECRM)

**Purpose:** Real-time onboard collision risk assessment and autonomous response

#### Data Inputs
- **Two-Line Elements (TLEs):** Updated every 6-12 hours from NORAD/Space-Track
- **Satellite State Vector:** Current position, velocity, attitude from telemetry
- **Debris Catalog:** 34,000+ tracked objects with uncertainty ellipsoids
- **Optional Sensors:** LIDAR, radar, camera for enhanced local awareness

#### Risk Assessment Pipeline
```
┌─────────────────────────────────────────────────────┐
│ 1. TLE Update & Parse                               │
│    └─ Ephemeris time, orbital elements              │
└─────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────┐
│ 2. Propagate Debris Orbits (SGP4)                   │
│    └─ Predict position at conjunction time          │
└─────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────┐
│ 3. Compute Distance to Closest Approach (DOCA)      │
│    └─ Minimum separation distance                   │
└─────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────┐
│ 4. Calculate Collision Probability                  │
│    └─ Mahalanobis distance in uncertainty volume    │
│    └─ Industry-standard CA method                   │
└─────────────────────────────────────────────────────┘
            ↓
┌─────────────────────────────────────────────────────┐
│ 5. Decision Threshold Check                         │
│    └─ Pc > 1e-4 (1 in 10,000)?                     │
└─────────────────────────────────────────────────────┘
            ↓
    YES ✓              NO ✗
    ↓                  ↓
 Execute            Continue
 Maneuver           Monitoring
```

#### Collision Probability Calculation
```python
# Mahalanobis distance approach
DOCA = sqrt(dx² + dy² + dz²)  # closest approach distance

# Covariance matrix combines:
# - Primary satellite ephemeris uncertainty (1-3 km)
# - Debris position uncertainty (1-10 km)
# - Debris velocity uncertainty (0.1-1 km/s)

Pc = 2 * Φ(-Mahalanobis_distance / hard_body_radius)

where Φ = standard normal CDF
```

#### Autonomous Response Levels

| Risk Level | Pc Range | Action | Latency |
|---|---|---|---|
| **CRITICAL** | > 1e-2 | Immediate maneuver + alert ground | < 100ms |
| **HIGH** | 1e-3 to 1e-2 | Prepare maneuver + alert | < 500ms |
| **MEDIUM** | 1e-4 to 1e-3 | Enhanced monitoring | < 1s |
| **LOW** | < 1e-4 | Routine TLE updates | 6-12h |

#### Hardware Requirements
- **Processor:** ARM Cortex-M4 or better
- **RAM:** 256-512 KB
- **ROM:** 1-2 MB (TLE storage + algorithms)
- **Power:** < 200 mW continuous
- **Real-time Loop:** 10 Hz (100ms decision cycle)

---

### 3️⃣ Predictive Validation & Simulation Dashboard (PVSD)

**Purpose:** Ground-based mission planning, maneuver validation, constellation analysis

#### Technology Stack
- **Backend:** Python (FastAPI/Flask) + PostgreSQL
- **Frontend:** React/Vue.js + Three.js/Cesium.js for 3D
- **Data Pipeline:** Apache Airflow for TLE ingestion
- **Visualization:** WebGL for real-time orbital rendering

#### Features

**A. Constellation Simulator**
- Import TLE catalogs (1 to 100,000+ satellites)
- Propagate orbits with SGP4/J2 perturbations
- Detect all conjunctions above configurable thresholds
- Visualize in 3D with interactive controls

**B. Maneuver Planner**
- Define collision threat scenario
- Compute optimal DDME posture sequence
- Simulate outcome: will maneuver work?
- Output confidence metrics

**C. What-If Analysis**
- "What if satellite mass increases?"
- "What if ADCS authority is reduced?"
- "What if maneuver starts 2 hours earlier?"
- Quantify impact on success probability

**D. Fuel Savings Calculator**
- Compare DDMS cost vs. traditional thrusters
- Input: satellite dry mass, mission duration, number of conjunctions
- Output: propellant saved ($M over mission life)

**E. Real-Time Monitoring**
- Dashboard shows:
  - Current satellite positions
  - Active maneuver status
  - Upcoming conjunction threats (24-72h window)
  - System health metrics

---

## Integration Points

### With Existing ADCS
```
ADCS Flight Computer
    ↓
  ├─ Attitude sensor data (gyros, sun sensors, star trackers)
  ├─ Actuator commands (magnetorquers, reaction wheels)
  ├─ Telemetry interface (CAN, RS-485, Ethernet)
  └─ TLE uplink capability
        ↓
    [AECRM + DDME Software]
        ↓
  ├─ Compute collision risk (every 100ms)
  ├─ Command protective postures
  ├─ Initiate maneuvers if threat detected
  └─ Log events & send health beacon
        ↓
    Ground Station
        ↓
  PVSD Dashboard (visualization & planning)
```

### API Interfaces

**Satellite-to-Ground:**
- CCSDS Telecommand Protocol for TLE uploads
- Beacon with maneuver status every 10 minutes
- Alert messages on critical events (< 100 bytes)

**Dashboard-to-Simulation:**
- REST API: `/api/simulate` (POST constellation + debris)
- WebSocket: `/ws/realtime` (live propagation updates)
- File I/O: Import/export TLE, scenario configs

---

## Scaling Considerations

### Single Satellite
- DDME + AECRM run continuously
- TLE updates from ground every 12 hours
- Minimal ground station involvement

### Constellation (10-1000 satellites)
- PVSD simulates coordinated maneuvers
- Detect maneuver conflicts (both satellites can't maneuver same time)
- Coordinate via ground or inter-satellite links
- Shared debris catalog reduces redundant computation

### Mega-Constellation (10,000+ satellites)
- Cloud-based PVSD with distributed computing
- Real-time TLE streaming to all satellites
- AI-powered threat prioritization
- Active debris removal mission planning

---

## Failure Modes & Resilience

| Failure | Impact | Recovery |
|---|---|---|
| ADCS unavailable | Cannot maneuver | Passive risk, alert ground |
| TLE data stale | Reduced prediction accuracy | Use last-known ephemeris |
| Microcontroller crash | Loss of autonomous response | Watchdog timer reboot |
| Communication loss | Cannot receive new TLEs | Use cached data for 3-7 days |
| Debris catalog incomplete | May miss threats | Supplement with sensor data |

---

## References & Standards

- **SGP4 Orbit Propagation:** Vallado, Crawford, Hujsa (2006)
- **Conjunction Assessment:** NASA CARA CDM (Conjunction Data Message)
- **Atmospheric Drag:** MSISE-90/00 Model
- **ADCS Standards:** CCSDS Attitude Data Conventions
- **TLE Format:** NORAD Two-Line Element Set Format

