#include "WingKinematics.h"
#include <math.h>

WingKinematics::WingKinematics()
    : _leftPin(PIN_SERVO_LEFT),
      _rightPin(PIN_SERVO_RIGHT),
      _currentState(KINEMATIC_SLEEP),
      _stateStartTime(0),
      _lastUpdateTime(0),
      _frequency(FREQ_BREATHE),
      _amplitude(6.0f),
      _centerAngle(SERVO_REST_ANGLE),
      _phaseOffset(0.0f),
      _currentLeftAngle(SERVO_REST_ANGLE),
      _currentRightAngle(SERVO_REST_ANGLE),
      _normalizedStroke(1.0f) {}

void WingKinematics::begin(int leftPin, int rightPin) {
    _leftPin = leftPin;
    _rightPin = rightPin;

    ESP32PWM::allocateTimer(0);
    ESP32PWM::allocateTimer(1);

    _servoLeft.setPeriodHertz(50);
    _servoRight.setPeriodHertz(50);

    _servoLeft.attach(_leftPin, 500, 2500);
    _servoRight.attach(_rightPin, 500, 2500);

    setState(KINEMATIC_BREATHING);
}

void WingKinematics::setState(KinematicState newState) {
    _currentState = newState;
    _stateStartTime = millis();

    switch (_currentState) {
        case KINEMATIC_SLEEP:
            _frequency = 0.0f;
            _amplitude = 0.0f;
            _centerAngle = SERVO_REST_ANGLE;
            break;

        case KINEMATIC_BREATHING:
            _frequency = FREQ_BREATHE;
            _amplitude = 8.0f;
            _centerAngle = 60.0f;
            break;

        case KINEMATIC_FLUTTER:
            _frequency = FREQ_GENTLE_FLUTTER;
            _amplitude = 25.0f;
            _centerAngle = 45.0f;
            break;

        case KINEMATIC_ACTIVE_FLIGHT:
            _frequency = FREQ_ACTIVE_FLIGHT;
            _amplitude = 30.0f;
            _centerAngle = 45.0f;
            break;

        case KINEMATIC_STARTLED:
            _frequency = FREQ_STARTLED;
            _amplitude = 32.0f;
            _centerAngle = 45.0f;
            break;

        case KINEMATIC_GLIDE:
            _frequency = 0.2f;
            _amplitude = 3.0f;
            _centerAngle = 25.0f;
            break;

        case KINEMATIC_CUSTOM:
            // Custom parameters preserved
            break;
    }
}

void WingKinematics::setParameters(float frequencyHz, float amplitudeDeg, float centerAngleDeg, float phaseOffsetRad) {
    _currentState = KINEMATIC_CUSTOM;
    _frequency = frequencyHz;
    _amplitude = amplitudeDeg;
    _centerAngle = centerAngleDeg;
    _phaseOffset = phaseOffsetRad;
}

void WingKinematics::update(unsigned long currentMillis) {
    if (_currentState == KINEMATIC_SLEEP) {
        applyTargetAngles(SERVO_REST_ANGLE, SERVO_REST_ANGLE);
        _normalizedStroke = 1.0f;
        return;
    }

    // Auto-transition out of STARTLED burst after 2.5 seconds
    if (_currentState == KINEMATIC_STARTLED && (currentMillis - _stateStartTime > 2500)) {
        setState(KINEMATIC_FLUTTER);
    }

    float t = (currentMillis - _stateStartTime) / 1000.0f;

    // Harmonic Biomimetic Kinematics:
    // Primary sine wave + subtle 2nd harmonic for biologically realistic wing acceleration
    float harmonic1 = sinf(2.0f * (float)M_PI * _frequency * t);
    float harmonic2 = 0.22f * sinf(4.0f * (float)M_PI * _frequency * t + 0.35f);
    float strokeVal = harmonic1 + harmonic2;

    // Normalized stroke: 0.0 (bottom of downstroke) to 1.0 (top of upstroke)
    _normalizedStroke = (strokeVal + 1.22f) / 2.44f;
    _normalizedStroke = constrain(_normalizedStroke, 0.0f, 1.0f);

    float targetAngleL = _centerAngle + (_amplitude * strokeVal);
    // Right wing motion with optional micro phase offset for natural asymmetry
    float strokeValR = sinf(2.0f * (float)M_PI * _frequency * t + _phaseOffset);
    float targetAngleR = _centerAngle + (_amplitude * strokeValR);

    // Clamp strictly within physical limits to protect gear train
    targetAngleL = constrain(targetAngleL, (float)SERVO_MIN_ANGLE, (float)SERVO_MAX_ANGLE);
    targetAngleR = constrain(targetAngleR, (float)SERVO_MIN_ANGLE, (float)SERVO_MAX_ANGLE);

    applyTargetAngles(targetAngleL, targetAngleR);
}

void WingKinematics::applyTargetAngles(float leftTarget, float rightTarget) {
    // Symmetrical mechanical mounting: Left and Right servos are mirrored
    // Left servo: higher angle = wings up
    // Right servo: mirrored orientation requires (180 - angle) or direct inverted mapping
    _currentLeftAngle = leftTarget;
    _currentRightAngle = rightTarget;

    _servoLeft.write((int)_currentLeftAngle);
    // Mirrored output for right servo
    int mirroredRight = 180 - (int)_currentRightAngle;
    _servoRight.write(mirroredRight);
}
