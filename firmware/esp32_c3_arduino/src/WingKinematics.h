#pragma once
#include <Arduino.h>
#include <ESP32Servo.h>
#include "Config.h"

enum KinematicState {
    KINEMATIC_SLEEP = 0,
    KINEMATIC_BREATHING,
    KINEMATIC_FLUTTER,
    KINEMATIC_ACTIVE_FLIGHT,
    KINEMATIC_STARTLED,
    KINEMATIC_GLIDE,
    KINEMATIC_CUSTOM
};

class WingKinematics {
public:
    WingKinematics();
    void begin(int leftPin = PIN_SERVO_LEFT, int rightPin = PIN_SERVO_RIGHT);
    void update(unsigned long currentMillis);
    
    void setState(KinematicState newState);
    KinematicState getState() const { return _currentState; }
    
    // Custom kinematic parameter overrides
    void setParameters(float frequencyHz, float amplitudeDeg, float centerAngleDeg, float phaseOffsetRad = 0.0f);
    
    // Direct angle getters
    float getLeftAngle() const { return _currentLeftAngle; }
    float getRightAngle() const { return _currentRightAngle; }
    float getNormalizedStroke() const { return _normalizedStroke; } // 0.0 (down) to 1.0 (up)

private:
    Servo _servoLeft;
    Servo _servoRight;
    int _leftPin;
    int _rightPin;
    
    KinematicState _currentState;
    unsigned long _stateStartTime;
    unsigned long _lastUpdateTime;
    
    // Motion variables
    float _frequency;
    float _amplitude;
    float _centerAngle;
    float _phaseOffset;
    
    float _currentLeftAngle;
    float _currentRightAngle;
    float _normalizedStroke;
    
    void applyTargetAngles(float leftTarget, float rightTarget);
};
