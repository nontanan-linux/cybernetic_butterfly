#pragma once
#include <Arduino.h>
#include "Config.h"

#ifndef PIN_TOUCH_ANT_L
#define PIN_TOUCH_ANT_L         0
#endif
#ifndef PIN_TOUCH_ANT_R
#define PIN_TOUCH_ANT_R         1
#endif
#ifndef TOUCH_BASELINE_SAMPLES
#define TOUCH_BASELINE_SAMPLES  32
#endif
#ifndef TOUCH_TRIGGER_DELTA
#define TOUCH_TRIGGER_DELTA     80
#endif

class TouchSensor {
public:
    TouchSensor(int pinAntennaL = PIN_TOUCH_ANT_L, int pinAntennaR = PIN_TOUCH_ANT_R);
    void begin();
    bool update(); // Returns true if touch was triggered this cycle
    
    bool isTouched() const { return _isTouched; }
    int getDeltaL() const { return _deltaL; }
    int getDeltaR() const { return _deltaR; }

private:
    int _pinL;
    int _pinR;
    
    float _baselineL;
    float _baselineR;
    int _deltaL;
    int _deltaR;
    bool _isTouched;
    unsigned long _lastTouchTime;
    
    int readCapacitanceSample(int pin);
};
