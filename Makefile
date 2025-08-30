# Makefile for mmSolver build and test interface.
#
# Usage:
#   make build_2024   - Build for Maya 2024
#   make test_2024    - Test for Maya 2024
#   make clean_2024   - Clean build files for Maya 2024
#

# This allows arguments to be passed to underlying scripts.
%:
	@:

.PHONY: help \
	build_2018 build_2019 build_2020 build_2022 build_2023 build_2024 build_2025 build_2026 \
	test_2018 test_2019 test_2020 test_2022 test_2023 test_2024 test_2025 test_2026 \
	clean_mmSolver_2018 clean_mmSolver_2019 clean_mmSolver_2020 clean_mmSolver_2022 clean_mmSolver_2023 clean_mmSolver_2024 clean_mmSolver_2025 clean_mmSolver_2026 \
	clean_openColorIO_2018 clean_openColorIO_2019 clean_openColorIO_2020 clean_openColorIO_2022 clean_openColorIO_2023 clean_openColorIO_2024 clean_openColorIO_2025 clean_openColorIO_2026 \
	clean_2018 clean_2019 clean_2020 clean_2022 clean_2023 clean_2024 clean_2025 clean_2026

# Default target.
help:
	@echo "mmSolver Build and Test interface."
	@echo ""
	@echo "Build targets:"
	@echo "  build_2018    Build for Maya 2018"
	@echo "  build_2019    Build for Maya 2019"
	@echo "  build_2020    Build for Maya 2020"
	@echo "  build_2022    Build for Maya 2022"
	@echo "  build_2023    Build for Maya 2023"
	@echo "  build_2024    Build for Maya 2024"
	@echo "  build_2025    Build for Maya 2025"
	@echo "  build_2026    Build for Maya 2026"
	@echo ""
	@echo "Test targets:"
	@echo "  test_2018     Test for Maya 2018"
	@echo "  test_2019     Test for Maya 2019"
	@echo "  test_2020     Test for Maya 2020"
	@echo "  test_2022     Test for Maya 2022"
	@echo "  test_2023     Test for Maya 2023"
	@echo "  test_2024     Test for Maya 2024"
	@echo "  test_2025     Test for Maya 2025"
	@echo "  test_2026     Test for Maya 2026"
	@echo ""
	@echo "Clean all targets:"
	@echo "  clean_2018              Clean all builds for Maya 2018"
	@echo "  clean_2019              Clean all builds for Maya 2019"
	@echo "  clean_2020              Clean all builds for Maya 2020"
	@echo "  clean_2022              Clean all builds for Maya 2022"
	@echo "  clean_2023              Clean all builds for Maya 2023"
	@echo "  clean_2024              Clean all builds for Maya 2024"
	@echo "  clean_2025              Clean all builds for Maya 2025"
	@echo "  clean_2026              Clean all builds for Maya 2026"
	@echo ""
	@echo "Clean mmSolver targets:"
	@echo "  clean_mmSolver_2018     Clean mmSolver build for Maya 2018"
	@echo "  clean_mmSolver_2019     Clean mmSolver build for Maya 2019"
	@echo "  clean_mmSolver_2020     Clean mmSolver build for Maya 2020"
	@echo "  clean_mmSolver_2022     Clean mmSolver build for Maya 2022"
	@echo "  clean_mmSolver_2023     Clean mmSolver build for Maya 2023"
	@echo "  clean_mmSolver_2024     Clean mmSolver build for Maya 2024"
	@echo "  clean_mmSolver_2025     Clean mmSolver build for Maya 2025"
	@echo "  clean_mmSolver_2026     Clean mmSolver build for Maya 2026"
	@echo ""
	@echo "Clean OpenColorIO targets:"
	@echo "  clean_openColorIO_2018  Clean OpenColorIO build for Maya 2018"
	@echo "  clean_openColorIO_2019  Clean OpenColorIO build for Maya 2019"
	@echo "  clean_openColorIO_2020  Clean OpenColorIO build for Maya 2020"
	@echo "  clean_openColorIO_2022  Clean OpenColorIO build for Maya 2022"
	@echo "  clean_openColorIO_2023  Clean OpenColorIO build for Maya 2023"
	@echo "  clean_openColorIO_2024  Clean OpenColorIO build for Maya 2024"
	@echo "  clean_openColorIO_2025  Clean OpenColorIO build for Maya 2025"
	@echo "  clean_openColorIO_2026  Clean OpenColorIO build for Maya 2026"
	@echo ""
	@echo "Examples:"
	@echo "  make build_2024"
	@echo "  make test_2024"
	@echo "  make test_2024 tests/test/test_api/test_solve_robotArm.py"
	@echo "  make clean_2024"
	@echo "  make clean_mmSolver_2024"
	@echo "  make clean_openColorIO_2024"

# Build targets.
build_2018:
	bash scripts/build_mmSolver_linux_maya2018.bash

build_2019:
	bash scripts/build_mmSolver_linux_maya2019.bash

build_2020:
	bash scripts/build_mmSolver_linux_maya2020.bash

build_2022:
	bash scripts/build_mmSolver_linux_maya2022.bash

build_2023:
	bash scripts/build_mmSolver_linux_maya2023.bash

build_2024:
	bash scripts/build_mmSolver_linux_maya2024.bash

build_2025:
	bash scripts/build_mmSolver_linux_maya2025.bash

build_2026:
	bash scripts/build_mmSolver_linux_maya2026.bash

# Test targets.
test_2018:
	bash scripts/test_mmSolver_linux_maya2018.bash $(filter-out $@,$(MAKECMDGOALS))

test_2019:
	bash scripts/test_mmSolver_linux_maya2019.bash $(filter-out $@,$(MAKECMDGOALS))

test_2020:
	bash scripts/test_mmSolver_linux_maya2020.bash $(filter-out $@,$(MAKECMDGOALS))

test_2022:
	bash scripts/test_mmSolver_linux_maya2022.bash $(filter-out $@,$(MAKECMDGOALS))

test_2023:
	bash scripts/test_mmSolver_linux_maya2023.bash $(filter-out $@,$(MAKECMDGOALS))

test_2024:
	bash scripts/test_mmSolver_linux_maya2024.bash $(filter-out $@,$(MAKECMDGOALS))

test_2025:
	bash scripts/test_mmSolver_linux_maya2025.bash $(filter-out $@,$(MAKECMDGOALS))

test_2026:
	bash scripts/test_mmSolver_linux_maya2026.bash $(filter-out $@,$(MAKECMDGOALS))

# Clean all targets.
clean_2018:
	$(MAKE) clean_openColorIO_2018
	$(MAKE) clean_mmSolver_2018

clean_2019:
	$(MAKE) clean_openColorIO_2019
	$(MAKE) clean_mmSolver_2019

clean_2020:
	$(MAKE) clean_openColorIO_2020
	$(MAKE) clean_mmSolver_2020

clean_2022:
	$(MAKE) clean_openColorIO_2022
	$(MAKE) clean_mmSolver_2022

clean_2023:
	$(MAKE) clean_openColorIO_2023
	$(MAKE) clean_mmSolver_2023

clean_2024:
	$(MAKE) clean_openColorIO_2024
	$(MAKE) clean_mmSolver_2024

clean_2025:
	$(MAKE) clean_openColorIO_2025
	$(MAKE) clean_mmSolver_2025

clean_2026:
	$(MAKE) clean_openColorIO_2026
	$(MAKE) clean_mmSolver_2026

# Clean mmSolver targets.
clean_mmSolver_2018:
	bash scripts/clean_mmSolver_linux_maya2018.bash

clean_mmSolver_2019:
	bash scripts/clean_mmSolver_linux_maya2019.bash

clean_mmSolver_2020:
	bash scripts/clean_mmSolver_linux_maya2020.bash

clean_mmSolver_2022:
	bash scripts/clean_mmSolver_linux_maya2022.bash

clean_mmSolver_2023:
	bash scripts/clean_mmSolver_linux_maya2023.bash

clean_mmSolver_2024:
	bash scripts/clean_mmSolver_linux_maya2024.bash

clean_mmSolver_2025:
	bash scripts/clean_mmSolver_linux_maya2025.bash

clean_mmSolver_2026:
	bash scripts/clean_mmSolver_linux_maya2026.bash

# Clean OpenColorIO targets.
clean_openColorIO_2018:
	bash scripts/clean_openColorIO_linux_maya2018.bash

clean_openColorIO_2019:
	bash scripts/clean_openColorIO_linux_maya2019.bash

clean_openColorIO_2020:
	bash scripts/clean_openColorIO_linux_maya2020.bash

clean_openColorIO_2022:
	bash scripts/clean_openColorIO_linux_maya2022.bash

clean_openColorIO_2023:
	bash scripts/clean_openColorIO_linux_maya2023.bash

clean_openColorIO_2024:
	bash scripts/clean_openColorIO_linux_maya2024.bash

clean_openColorIO_2025:
	bash scripts/clean_openColorIO_linux_maya2025.bash

clean_openColorIO_2026:
	bash scripts/clean_openColorIO_linux_maya2026.bash
