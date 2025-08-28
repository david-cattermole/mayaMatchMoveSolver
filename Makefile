# Makefile for mmSolver build and test shortcuts
#
# Usage:
#   make build_2024                    - Build for Maya 2024
#   make test_2024                     - Test for Maya 2024
#   make test_2024 path/to/test.py     - Test specific file for Maya 2024
#

# This allows arguments to be passed to underlying scripts
%:
	@:

.PHONY: help \
	build_2018 build_2019 build_2020 build_2022 build_2023 build_2024 build_2025 build_2026 \
	test_2018 test_2019 test_2020 test_2022 test_2023 test_2024 test_2025 test_2026

# Default target
help:
	@echo "mmSolver Build and Test Shortcuts"
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
	@echo "Examples:"
	@echo "  make build_2024"
	@echo "  make test_2024"
	@echo "  make test_2024 tests/test/test_api/test_solve_robotArm.py"

# Build targets
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

# Test targets
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
