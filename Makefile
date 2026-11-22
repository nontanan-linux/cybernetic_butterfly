# =============================================================================
# ElectronicsArt — Unified Project Makefile
# =============================================================================

PYTHON ?= python

.PHONY: all help build cad pcb sync sim sim-all view clean

all: help

help:
	@echo "=================================================================="
	@echo "🦋 ElectronicsArt — Command Quick Reference"
	@echo "=================================================================="
	@echo "  make build      Build all 3D CAD models, PCB Art SVG & sync configs"
	@echo "  make cad        Build only 3D CAD models (STL & STEP solids)"
	@echo "  make pcb        Build only 2D PCB Art SVG vector layers"
	@echo "  make sync       Synchronize unified YAML configs across C++, Python & Web"
	@echo "  make sim        Run kinematics & power simulation (flutter mode)"
	@echo "  make sim-all    Run simulation across all 6 behavioral modes"
	@echo "  make view       Launch 3D WebGL visualizer server (Three.js)"
	@echo "  make clean      Clean generated build artifacts"
	@echo "=================================================================="

build:
	$(PYTHON) scripts/build_model.py

cad:
	$(PYTHON) scripts/build_model.py --cad-only

pcb:
	$(PYTHON) scripts/build_model.py --pcb-only

sync:
	$(PYTHON) scripts/sync_config.py

sim:
	$(PYTHON) scripts/simulate_kinematics.py --power --plot

sim-all:
	$(PYTHON) scripts/simulate_kinematics.py --mode all

view:
	$(PYTHON) scripts/visualize_model.py

clean:
	$(PYTHON) scripts/build_model.py --clean
