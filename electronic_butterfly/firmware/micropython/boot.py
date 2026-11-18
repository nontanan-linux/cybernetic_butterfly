# boot.py -- executed on ESP32-C3 boot-up
import esp
esp.osdebug(None)
import gc
gc.collect()
print("Boot complete. Ready for Cybernetic Butterfly execution.")
