#include "TouchSensor.h"

TouchSensor::TouchSensor(int pinAntennaL, int pinAntennaR)
    : _pinL(pinAntennaL),
      _pinR(pinAntennaR),
      _baselineL(0.0f),
      _baselineR(0.0f),
      _deltaL(0),
      _deltaR(0),
      _isTouched(false),
      _lastTouchTime(0) {}

void TouchSensor::begin() {
    analogReadResolution(12);

    // Initial calibration: establish baseline over multiple samples
    long sumL = 0;
    long sumR = 0;
    for (int i = 0; i < TOUCH_BASELINE_SAMPLES; i++) {
        sumL += readCapacitanceSample(_pinL);
        sumR += readCapacitanceSample(_pinR);
        delay(3);
    }
    _baselineL = (float)sumL / TOUCH_BASELINE_SAMPLES;
    _baselineR = (float)sumR / TOUCH_BASELINE_SAMPLES;
}

int TouchSensor::readCapacitanceSample(int pin) {
    // Relaxation charge/discharge cycle:
    // 1. Charge antenna probe via digital output HIGH
    pinMode(pin, OUTPUT);
    digitalWrite(pin, HIGH);
    delayMicroseconds(10);

    // 2. Switch to high-impedance input and read residual voltage
    pinMode(pin, INPUT);
    delayMicroseconds(5);
    int val = analogRead(pin);

    // 3. Discharge probe to ground to reset
    pinMode(pin, OUTPUT);
    digitalWrite(pin, LOW);
    delayMicroseconds(5);
    pinMode(pin, INPUT);

    return val;
}

bool TouchSensor::update() {
    int sampleL = readCapacitanceSample(_pinL);
    int sampleR = readCapacitanceSample(_pinR);

    // Calculate deviations from baseline
    _deltaL = abs(sampleL - (int)_baselineL);
    _deltaR = abs(sampleR - (int)_baselineR);

    // Slow baseline auto-tracking filter (adapts to ambient humidity/temperature drift)
    _baselineL = (_baselineL * 0.98f) + (sampleL * 0.02f);
    _baselineR = (_baselineR * 0.98f) + (sampleR * 0.02f);

    bool currentTouch = (_deltaL > TOUCH_TRIGGER_DELTA || _deltaR > TOUCH_TRIGGER_DELTA);

    // Debounce touch events (minimum 350ms between re-triggers)
    unsigned long now = millis();
    if (currentTouch && !_isTouched && (now - _lastTouchTime > 350)) {
        _isTouched = true;
        _lastTouchTime = now;
        return true;
    }

    if (!currentTouch) {
        _isTouched = false;
    }

    return false;
}
