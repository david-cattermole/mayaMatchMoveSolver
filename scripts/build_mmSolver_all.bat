@ECHO OFF
SETLOCAL
::
:: Copyright (C) 2025 David Cattermole.
::
:: This file is part of mmSolver.
::
:: mmSolver is free software: you can redistribute it and/or modify it
:: under the terms of the GNU Lesser General Public License as
:: published by the Free Software Foundation, either version 3 of the
:: License, or (at your option) any later version.
::
:: mmSolver is distributed in the hope that it will be useful,
:: but WITHOUT ANY WARRANTY; without even the implied warranty of
:: MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
:: GNU Lesser General Public License for more details.
::
:: You should have received a copy of the GNU Lesser General Public License
:: along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
:: ---------------------------------------------------------------------
::
:: Builds the Maya MatchMove Solver project for all supported
:: operating systems, with Windows as a host operating system.

set PROJECT_ROOT=%~dp0

:: Windows - Maya 2020 Build
call scripts/build_mmSolver_windows64_maya2020.bat

:: Windows - Maya 2022 Build
call scripts/build_mmSolver_windows64_maya2022.bat

:: Windows - Maya 2023 Build
call scripts/build_mmSolver_windows64_maya2023.bat

:: Windows - Maya 2024 Build
call scripts/build_mmSolver_windows64_maya2024.bat

:: Windows - Maya 2025 Build
call scripts/build_mmSolver_windows64_maya2025.bat

:: Linux - Maya 2019 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2019" -t mmsolver-linux-maya2019-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2019-build "bash -c './scripts/build_mmSolver_linux_maya2019.bash'"

:: Linux - Maya 2020 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2020" -t mmsolver-linux-maya2020-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2020-build "bash -c './scripts/build_mmSolver_linux_maya2020.bash'"

:: Linux - Maya 2022 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2022" -t mmsolver-linux-maya2022-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2022-build "bash -c './scripts/build_mmSolver_linux_maya2022.bash'"

:: Linux - Maya 2023 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2023" -t mmsolver-linux-maya2023-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2023-build "bash -c './scripts/build_mmSolver_linux_maya2023.bash'"

:: Linux - Maya 2024 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2024" -t mmsolver-linux-maya2024-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2024-build "bash -c './scripts/build_mmSolver_linux_maya2024.bash'"

:: Linux - Maya 2025 Build
docker buildx build --file "%PROJECT_ROOT%share\docker\Dockerfile_maya2025" -t mmsolver-linux-maya2025-build "%PROJECT_ROOT%"
docker container run --volume "%PROJECT_ROOT%:/mmSolver" mmsolver-linux-maya2025-build "bash -c './scripts/build_mmSolver_linux_maya2025.bash'"
