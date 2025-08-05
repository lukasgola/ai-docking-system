# Methodological Framework for AGV Docking System Using Fuzzy Logic Control

## 1. Fuzzy Logic Controller Structure

### 1.1 Controller Architecture

The AGV docking system employs a **Mamdani-type fuzzy logic controller** implemented using the scikit-fuzzy library. The system utilizes a three-phase control strategy with distinct fuzzy controllers for different docking phases:

- **Phase 1 (FuzzyLogicController)**: Initial approach and positioning
- **Phase 2 (FuzzyRotateLogicController)**: Rotation and alignment
- **Phase 3 (FuzzyParallelLogicController)**: Final parallel approach

### 1.2 Inference Method and Defuzzification

The system uses **Mamdani inference** with **centroid defuzzification** method. The inference process follows these steps:

1. **Fuzzification**: Input sensor values are converted to membership degrees
2. **Rule Evaluation**: Fuzzy rules are evaluated using AND/OR operators
3. **Aggregation**: Multiple rule outputs are combined
4. **Defuzzification**: Centroid method converts fuzzy output to crisp values

## 2. Input and Output Variables

### 2.1 Input Variables

| Variable | Description                   | Range       | Units | Fuzzy Sets                                                 |
| -------- | ----------------------------- | ----------- | ----- | ---------------------------------------------------------- |
| `dist1`  | Distance from front sensor    | 0-700       | mm    | close (0-160), ok (150-300), far (250-700)                 |
| `dist2`  | Distance from left sensor     | 0-5000      | mm    | close (0-160), ok (150-300), far (250-5000)                |
| `dist3`  | Distance from right sensor    | 0-5000      | mm    | close (0-160), ok (150-300), far (250-5000)                |
| `diff`   | Distance difference (Phase 3) | -200 to 200 | mm    | negative (-200 to -1), zero (-2 to 2), positive (1 to 200) |

### 2.2 Output Variables

| Variable | Description       | Range      | Units     | Fuzzy Sets                                                         |
| -------- | ----------------- | ---------- | --------- | ------------------------------------------------------------------ |
| `speedL` | Left motor speed  | -50 to 50  | PWM units | back (-50 to 0), stop (-15 to 15), slow (0 to 30), fast (20 to 50) |
| `speedR` | Right motor speed | -50 to 100 | PWM units | back (-50 to 0), stop (-15 to 15), slow (0 to 30), fast (20 to 50) |

### 2.3 Membership Functions

**Distance Variables (dist1, dist2, dist3):**

- **Close**: Trapezoidal [0, 0, 150, 160] - represents distances requiring immediate action
- **Ok**: Trapezoidal [150, 200, 250, 300] - represents acceptable distances
- **Far**: Trapezoidal [250, 300, 4900, 5000] - represents distances allowing forward movement

**Speed Variables (speedL, speedR):**

- **Back**: Trapezoidal [-50, -30, -15, 0] - reverse movement
- **Stop**: Trapezoidal [-15, -5, 5, 15] - no movement
- **Slow**: Trapezoidal [0, 10, 20, 30] - slow forward movement
- **Fast**: Trapezoidal [20, 30, 40, 50] - fast forward movement

### 2.4 Fuzzy Distance Categories Specification

To define the fuzzy categories used in our system, Table 1 summarizes the parameters of each distance term. These values are expressed in millimeters and reflect the empirical range observed using TOF sensors mounted on the AGV.

**Table 1. Fuzzy distance categories used in fuzzification of sensor input**

| Label | Core Range (μ = 1) | Support Range (μ > 0) | Shape       | Description                          |
| ----- | ------------------ | --------------------- | ----------- | ------------------------------------ |
| Close | 0 – 150 mm         | 0 – 160 mm            | Trapezoidal | Distances requiring immediate action |
| Ok    | 200 – 250 mm       | 150 – 300 mm          | Trapezoidal | Acceptable distances for navigation  |
| Far   | 300 – 4900 mm      | 250 – 5000 mm         | Trapezoidal | Distances allowing forward movement  |

**Table 2. Detailed membership function parameters for distance variables**

| Variable | Fuzzy Set | Core Range [mm] | Support Range [mm] | Trapezoidal Parameters [a,b,c,d] | Overlap Regions     |
| -------- | --------- | --------------- | ------------------ | -------------------------------- | ------------------- |
| dist1    | Close     | 0-150           | 0-160              | [0, 0, 150, 160]                 | 150-160 mm          |
|          | Ok        | 200-250         | 150-300            | [150, 200, 250, 300]             | 150-200, 250-300 mm |
|          | Far       | 300-600         | 250-700            | [250, 300, 600, 700]             | 250-300 mm          |
| dist2    | Close     | 0-150           | 0-160              | [0, 0, 150, 160]                 | 150-160 mm          |
|          | Ok        | 200-250         | 150-300            | [150, 200, 250, 300]             | 150-200, 250-300 mm |
|          | Far       | 300-4900        | 250-5000           | [250, 300, 4900, 5000]           | 250-300 mm          |
| dist3    | Close     | 0-150           | 0-160              | [0, 0, 150, 160]                 | 150-160 mm          |
|          | Ok        | 200-250         | 150-300            | [150, 200, 250, 300]             | 150-200, 250-300 mm |
|          | Far       | 300-4900        | 250-5000           | [250, 300, 4900, 5000]           | 250-300 mm          |

**Table 3. Distance difference categories for Phase 3 parallel approach**

| Label    | Core Range (μ = 1) | Support Range (μ > 0) | Shape       | Description                       |
| -------- | ------------------ | --------------------- | ----------- | --------------------------------- |
| Negative | -150 to -20 mm     | -200 to -1 mm         | Trapezoidal | Left offset requiring correction  |
| Zero     | -2 to 2 mm         | -2 to 2 mm            | Triangular  | Properly aligned                  |
| Positive | 20 to 150 mm       | 1 to 200 mm           | Trapezoidal | Right offset requiring correction |

These values were selected based on the response behavior of the AGV in the docking environment and allow for overlapping transitions between categories to ensure smooth control actions. The trapezoidal membership functions provide gradual transitions between fuzzy sets, preventing abrupt control changes that could cause jerky movements during docking maneuvers.

## 3. Sensor Data Handling

### 3.1 Data Acquisition

The system receives sensor data through UDP communication:

- **Protocol**: UDP socket communication
- **Frequency**: 100 Hz (10ms intervals)
- **Data Format**: String with semicolon-separated values "d1;d2;d3"
- **Units**: Distance measurements in millimeters

### 3.2 Data Processing Pipeline

1. **Raw Data Reception**: UDP packets received from sensor network
2. **Data Parsing**: String parsing to extract d1, d2, d3 values
3. **Data Validation**: Check for timeout and data integrity
4. **Fuzzy Input Assignment**: Direct assignment to fuzzy controller inputs
5. **Control Computation**: Fuzzy logic processing
6. **Output Generation**: Motor speed commands

### 3.3 Data Flow

```
Sensor Network → UDP Socket → Data Parser → Fuzzy Controller → Motor Commands
```

## 4. Fuzzy Rule Base

### 4.1 Phase 1 Rules (Initial Approach)

The system implements **12 primary rules** for the initial approach phase:

| Rule | Condition                                   | Action                   | Logic                         |
| ---- | ------------------------------------------- | ------------------------ | ----------------------------- |
| R1   | dist1=close AND dist2=close AND dist3=close | speedL=back, speedR=back | Emergency stop when too close |
| R2   | dist1=close AND dist2=close AND dist3=far   | speedL=slow, speedR=stop | Turn right to align           |
| R3   | dist1=close AND dist2=far AND dist3=far     | speedL=fast, speedR=fast | Move forward when clear       |
| R4   | dist1=far AND dist2=far AND dist3=far       | speedL=slow, speedR=fast | Turn left approach            |
| R5   | dist1=far AND dist2=far AND dist3=close     | speedL=slow, speedR=back | Avoid right obstacle          |
| R6   | dist1=far AND dist2=close AND dist3=close   | speedL=stop, speedR=stop | Stop when close to left       |
| R7   | dist1=far AND dist2=close AND dist3=ok      | speedL=back, speedR=stop | Back away from left           |
| R8   | dist1=far AND dist2=ok AND dist3=close      | speedL=stop, speedR=stop | Stop when close to right      |
| R9   | dist1=far AND dist2=ok AND dist3=far        | speedL=stop, speedR=slow | Turn right slowly             |
| R10  | dist1=far AND dist2=far AND dist3=ok        | speedL=fast, speedR=stop | Turn left approach            |
| R11  | dist1=far AND dist2=ok AND dist3=ok         | speedL=stop, speedR=stop | Stop when aligned             |
| R12  | dist1=far AND dist2=close AND dist3=far     | speedL=stop, speedR=slow | Avoid left obstacle           |

### 4.2 Phase 2 Rules (Rotation)

**10 rules** for rotation and alignment phase:

| Rule | Condition                               | Action                   | Logic             |
| ---- | --------------------------------------- | ------------------------ | ----------------- |
| R1   | dist1=far AND dist2=ok AND dist3=ok     | speedL=slow, speedR=back | Rotate left       |
| R2   | dist1=far AND dist2=close AND dist3=ok  | speedL=stop, speedR=back | Sharp left turn   |
| R3   | dist1=far AND dist2=ok AND dist3=close  | speedL=slow, speedR=back | Rotate left       |
| R4   | dist1=far AND dist2=close AND dist3=far | speedL=stop, speedL=back | Sharp left turn   |
| R5   | dist1=far AND dist2=ok AND dist3=far    | speedL=slow, speedR=back | Rotate left       |
| R6   | dist1=far AND dist2=far AND dist3=far   | speedL=slow, speedR=back | Rotate left       |
| R7   | dist1=ok AND dist2=ok AND dist3=far     | speedL=slow, speedR=stop | Fine adjustment   |
| R8   | dist1=close AND dist2=ok AND dist3=far  | speedL=slow, speedR=back | Fine adjustment   |
| R9   | dist1=ok AND dist2=far AND dist3=far    | speedL=stop, speedR=stop | Stop when aligned |
| R10  | dist1=close AND dist2=far AND dist3=far | speedL=stop, speedR=stop | Stop when aligned |

### 4.3 Phase 3 Rules (Parallel Approach)

**5 rules** for final parallel approach using distance difference:

| Rule | Condition                                          | Action                   | Logic                     |
| ---- | -------------------------------------------------- | ------------------------ | ------------------------- |
| R1   | diff=negative AND dist2=far AND dist3=far          | speedL=fast, speedR=slow | Correct left offset       |
| R2   | diff=negative AND dist2=ok AND dist3=far           | speedL=fast, speedR=slow | Correct left offset       |
| R3   | diff=zero AND dist2=far AND dist3=far              | speedL=fast, speedR=fast | Move forward when aligned |
| R4   | diff=positive AND dist2=far AND dist3=far          | speedL=slow, speedR=fast | Correct right offset      |
| R5   | dist2=close OR dist3=close OR dist2=ok OR dist3=ok | speedL=stop, speedR=stop | Stop when close           |

## 5. System Architecture and Data Flow

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Sensor Data   │───▶│  Data Parser    │───▶│  Mode Selector  │
│   (UDP Socket)  │    │  (d1,d2,d3)     │    │  (Phase 1/2/3)  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                                       │
                                                       ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Motor Output  │◀───│  Fuzzy Logic    │◀───│  Controller     │
│   (PWM Signal)  │    │  Processing     │    │  Selection      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │  Rule Base      │
                       │  (12/10/5 rules)│
                       └─────────────────┘
```

## 6. Worked Example

### 6.1 Example Scenario

Consider an AGV approaching a docking station with the following sensor readings:

- **dist1** = 400 mm (far from front)
- **dist2** = 180 mm (ok distance from left)
- **dist3** = 280 mm (ok distance from right)

### 6.2 Phase 1 Processing

1. **Fuzzification**:

   - dist1: μ_far(400) = 1.0, μ_ok(400) = 0.0, μ_close(400) = 0.0
   - dist2: μ_ok(180) = 0.8, μ_close(180) = 0.2, μ_far(180) = 0.0
   - dist3: μ_ok(280) = 0.6, μ_far(280) = 0.4, μ_close(280) = 0.0

2. **Rule Evaluation** (Rule 11 applies):

   - IF dist1=far AND dist2=ok AND dist3=ok THEN speedL=stop, speedR=stop
   - Rule strength: min(1.0, 0.8, 0.6) = 0.6

3. **Defuzzification**:
   - Output: speedL = 0, speedR = 0 (stop both motors)

### 6.3 Mode Transition

When dist2 > 250 and dist3 > 250, the system transitions to Phase 2 (rotation mode).

## 7. Control System Characteristics

### 7.1 Multi-Phase Control Strategy

The system employs a **state machine** with three distinct phases:

- **Phase 1**: Initial approach (distance-based navigation)
- **Phase 2**: Rotation and alignment (orientation correction)
- **Phase 3**: Parallel approach (fine positioning)

### 7.2 Real-Time Performance

- **Control Frequency**: 100 Hz
- **Response Time**: < 10ms
- **Data Latency**: < 1ms (UDP communication)

### 7.3 Robustness Features

- **Timeout Handling**: Graceful degradation on sensor failure
- **Data Validation**: Range checking for sensor inputs
- **Mode Transitions**: Smooth phase transitions based on distance thresholds

## 8. Conclusion

The fuzzy logic approach is particularly suitable for AGV docking applications due to its ability to handle **uncertainty and imprecision** in sensor measurements and environmental conditions. The **linguistic rule-based system** provides intuitive control that mimics human decision-making processes, while the **multi-phase control strategy** ensures precise docking through progressive refinement of the approach trajectory. The **Mamdani inference method** with centroid defuzzification provides smooth control outputs that prevent jerky movements and ensure stable docking performance under varying environmental conditions.
