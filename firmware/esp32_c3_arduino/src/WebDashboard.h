#pragma once
#include <Arduino.h>
#include <WiFi.h>
#include <WebServer.h>
#include "WingKinematics.h"
#include "LEDEffects.h"
#include "Config.h"

class WebDashboard {
public:
    WebDashboard(WingKinematics& kinematics, LEDEffects& ledEffects);
    void begin();
    void handleClient();

private:
    WebServer _server;
    WingKinematics& _kinematics;
    LEDEffects& _ledEffects;
    
    void handleRoot();
    void handleSetState();
    void handleSetPattern();
    void handleSetSpeed();
    void handleStatus();
};
