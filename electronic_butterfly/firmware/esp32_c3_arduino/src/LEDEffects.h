#pragma once
#include <Arduino.h>
#include <FastLED.h>
#include "Config.h"

enum LEDPattern {
    PATTERN_BIOLUMINESCENCE = 0,
    PATTERN_MORPHO_BLUE,
    PATTERN_MONARCH_FIRE,
    PATTERN_CYBER_AURORA,
    PATTERN_TOUCH_SURGE,
    PATTERN_OFF
};

class LEDEffects {
public:
    LEDEffects();
    void begin();
    void update(unsigned long currentMillis, float wingStrokeNormalized = 0.5f);
    
    void setPattern(LEDPattern newPattern);
    LEDPattern getPattern() const { return _currentPattern; }
    
    void triggerTouchSurge();
    void setBrightness(uint8_t brightness);

private:
    CRGB _leds[TOTAL_LEDS];
    LEDPattern _currentPattern;
    LEDPattern _previousPattern;
    unsigned long _lastUpdate;
    unsigned long _surgeStartTime;
    bool _isSurging;
    uint8_t _brightness;
    
    void renderBioluminescence(unsigned long ms);
    void renderMorphoBlue(unsigned long ms, float stroke);
    void renderMonarchFire(unsigned long ms);
    void renderCyberAurora(unsigned long ms);
    void renderTouchSurge(unsigned long ms);
};
