#include "LEDEffects.h"

LEDEffects::LEDEffects()
    : _currentPattern(PATTERN_BIOLUMINESCENCE),
      _previousPattern(PATTERN_BIOLUMINESCENCE),
      _lastUpdate(0),
      _surgeStartTime(0),
      _isSurging(false),
      _brightness(180) {}

void LEDEffects::begin() {
    FastLED.addLeds<WS2812B, PIN_WS2812B_DATA, GRB>(_leds, TOTAL_LEDS);
    FastLED.setBrightness(_brightness);
    FastLED.clear(true);
}

void LEDEffects::setBrightness(uint8_t brightness) {
    _brightness = brightness;
    FastLED.setBrightness(_brightness);
}

void LEDEffects::setPattern(LEDPattern newPattern) {
    _currentPattern = newPattern;
    _isSurging = false;
}

void LEDEffects::triggerTouchSurge() {
    _isSurging = true;
    _surgeStartTime = millis();
}

void LEDEffects::update(unsigned long currentMillis, float wingStrokeNormalized) {
    // 60 FPS update throttle (approx every 16ms)
    if (currentMillis - _lastUpdate < 16) return;
    _lastUpdate = currentMillis;

    if (_isSurging) {
        renderTouchSurge(currentMillis);
    } else {
        switch (_currentPattern) {
            case PATTERN_BIOLUMINESCENCE:
                renderBioluminescence(currentMillis);
                break;
            case PATTERN_MORPHO_BLUE:
                renderMorphoBlue(currentMillis, wingStrokeNormalized);
                break;
            case PATTERN_MONARCH_FIRE:
                renderMonarchFire(currentMillis);
                break;
            case PATTERN_CYBER_AURORA:
                renderCyberAurora(currentMillis);
                break;
            case PATTERN_OFF:
            default:
                FastLED.clear();
                break;
        }
    }

    FastLED.show();
}

void LEDEffects::renderBioluminescence(unsigned long ms) {
    // Aquatic deep-sea glowing pulse propagating outward along wing veins
    for (int i = 0; i < NUM_LEDS_PER_WING; i++) {
        uint8_t wave = sin8((ms / 7) - (i * 32));
        CRGB color = blend(CRGB(0, 160, 180), CRGB(16, 255, 120), wave);
        color.nscale8(wave);

        _leds[i] = color;                              // Left wing
        _leds[TOTAL_LEDS - 1 - i] = color;             // Mirrored right wing
    }
}

void LEDEffects::renderMorphoBlue(unsigned long ms, float stroke) {
    // Shimmering structural blue-violet, intensifies on upstroke
    uint8_t strokeBoost = (uint8_t)(stroke * 90.0f);
    for (int i = 0; i < NUM_LEDS_PER_WING; i++) {
        uint8_t shimmer = sin8((ms / 4) + (i * 45));
        CRGB baseColor = CRGB(0, 70, 255);             // Deep electric cobalt blue
        CRGB highlight = CRGB(180, 50, 255);           // Iridescent violet

        CRGB color = blend(baseColor, highlight, shimmer);
        color.fadeToBlackBy(shimmer < 120 ? 80 : 0);
        color += CRGB(strokeBoost / 2, strokeBoost, strokeBoost);

        _leds[i] = color;
        _leds[TOTAL_LEDS - 1 - i] = color;
    }
}

void LEDEffects::renderMonarchFire(unsigned long ms) {
    // Warm fire / ember ripple along veins with pure white margin stars
    for (int i = 0; i < NUM_LEDS_PER_WING; i++) {
        if (i == 3 || i == 7) {
            // Margin tip spots (monarch white stars)
            uint8_t twinkle = sin8((ms / 3) + (i * 60));
            _leds[i] = CRGB(twinkle, twinkle, twinkle);
            _leds[TOTAL_LEDS - 1 - i] = CRGB(twinkle, twinkle, twinkle);
        } else {
            // Main vein fire pulse
            uint8_t heat = sin8((ms / 6) + (i * 28));
            CRGB flame = blend(CRGB(255, 60, 0), CRGB(255, 190, 0), heat);
            flame.nscale8(heat);
            _leds[i] = flame;
            _leds[TOTAL_LEDS - 1 - i] = flame;
        }
    }
}

void LEDEffects::renderCyberAurora(unsigned long ms) {
    // Multi-color organic chromatic gradient sweeping across wings
    for (int i = 0; i < TOTAL_LEDS; i++) {
        uint8_t hue = (ms / 15) + (i * 12);
        _leds[i] = CHSV(hue, 220, 230);
    }
}

void LEDEffects::renderTouchSurge(unsigned long ms) {
    unsigned long elapsed = ms - _surgeStartTime;
    if (elapsed > 1200) {
        _isSurging = false;
        return;
    }

    // High energy shockwave expanding outward from thorax
    int activeIndex = (int)(elapsed / 75);
    for (int i = 0; i < NUM_LEDS_PER_WING; i++) {
        if (i == activeIndex) {
            _leds[i] = CRGB::White;
            _leds[TOTAL_LEDS - 1 - i] = CRGB::White;
        } else if (i < activeIndex) {
            _leds[i] = CRGB(0, 220, 255);
            _leds[TOTAL_LEDS - 1 - i] = CRGB(0, 220, 255);
            _leds[i].fadeToBlackBy(120);
            _leds[TOTAL_LEDS - 1 - i].fadeToBlackBy(120);
        } else {
            _leds[i] = CRGB::Black;
            _leds[TOTAL_LEDS - 1 - i] = CRGB::Black;
        }
    }
}
