/*
 * Copyright (C) 2024 David Cattermole.
 *
 * This file is part of mmSolver.
 *
 * mmSolver is free software: you can redistribute it and/or modify it
 * under the terms of the GNU Lesser General Public License as
 * published by the Free Software Foundation, either version 3 of the
 * License, or (at your option) any later version.
 *
 * mmSolver is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU Lesser General Public License for more details.
 *
 * You should have received a copy of the GNU Lesser General Public License
 * along with mmSolver.  If not, see <https://www.gnu.org/licenses/>.
 * ====================================================================
 *
 */

#include "memory_system_utils.h"

// STL
#include <fstream>   // ifstream
#include <ios>       // ios_base
#include <iostream>  // cout, cerr, endl
#include <sstream>   // stringstream

// OS-specific headers.
#ifdef _WIN32  // Windows MSVC
#include <windows.h>
// windows.h must be defined first.
#include <psapi.h>
#else                     // Linux and MacOS
#include <sys/stat.h>     // stat (check a file exists)
#include <sys/sysinfo.h>  // sysinfo
#include <sys/types.h>    // uint32_t, uint64_t, etc
#include <unistd.h>       // sysconf
#endif

namespace mmmemorysystem {

// Get the current process's memory usage.
//
// Takes two size_t by reference, attempts to read the
// system-dependent data for a process' virtual memoryUsed size and
// resident set size, and return the results in bytes.
//
// On failure, returns 0, 0
//
// http://stackoverflow.com/questions/669438/how-to-get-memory-usage-at-run-time-in-c
void process_memory_usage(size_t &peak_resident_set_size,
                          size_t &current_resident_set_size) {
    peak_resident_set_size = 0;
    current_resident_set_size = 0;

#ifdef _WIN32  // Windows MSVC
    PROCESS_MEMORY_COUNTERS info;
    GetProcessMemoryInfo(GetCurrentProcess(), &info, sizeof(info));

    // TODO: We could get the "PrivateUsage" on Windows as this is
    // what is displayed in the Windows Task Manager?
    // https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process/
    current_resident_set_size = static_cast<size_t>(info.WorkingSetSize);
    peak_resident_set_size = static_cast<size_t>(info.PeakWorkingSetSize);
#else  // Linux and MacOS
    // 'file' stat seems to give the most reliable results
    std::ifstream stat_stream("/proc/self/stat", std::ios_base::in);

    // dummy vars for leading entries in stat that we don't care about
    std::string pid, comm, state, ppid, pgrp, session, tty_nr;
    std::string tpgid, flags, minflt, cminflt, majflt, cmajflt;
    std::string utime, stime, cutime, cstime, priority, nice;
    std::string O, itrealvalue, starttime;

    // the two fields we want
    size_t vsize;
    size_t rss;

    stat_stream >> pid >> comm >> state >> ppid >> pgrp >> session >> tty_nr >>
        tpgid >> flags >> minflt >> cminflt >> majflt >> cmajflt >> utime >>
        stime >> cutime >> cstime >> priority >> nice >> O >> itrealvalue >>
        starttime >> vsize >> rss;  // don't care about the rest
    stat_stream.close();

    // In case of x86-64, page size is configured to use 2MB pages.
    const size_t page_size = static_cast<size_t>(sysconf(_SC_PAGE_SIZE));
    peak_resident_set_size = vsize;
    current_resident_set_size = rss * page_size;
#endif
    return;
}

// Get the all the physical RAM available to the OS, in bytes.
//
// How to get the amount of (CPU) system memory?
// https://stackoverflow.com/questions/2513505/how-to-get-available-memory-c-g
// https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process/
size_t system_physical_memory_total() {
#ifdef _WIN32  // Windows MSVC
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);

    size_t total_physical_memory_bytes = status.ullTotalPhys;
    return total_physical_memory_bytes;
#else  // Linux and MacOS
    // https://www.man7.org/linux/man-pages/man2/sysinfo.2.html
    struct sysinfo memInfo;
    sysinfo(&memInfo);

    size_t total_physical_memory_bytes = memInfo.totalram;
    // Multiply to avoid int overflow on right hand side.
    total_physical_memory_bytes *= memInfo.mem_unit;

    return total_physical_memory_bytes;
#endif
}

// Returns memory bytes used.
//
// https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process/
size_t system_physical_memory_used() {
#ifdef _WIN32  // Windows MSVC
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);

    size_t physical_memory_used_bytes =
        status.ullTotalPhys - status.ullAvailPhys;
    return physical_memory_used_bytes;
#else  // Linux and MacOS
    // https://www.man7.org/linux/man-pages/man2/sysinfo.2.html
    struct sysinfo memInfo;
    sysinfo(&memInfo);

    size_t physical_memory_used_bytes = memInfo.totalram - memInfo.freeram;
    // Multiply to avoid int overflow on right hand side.
    physical_memory_used_bytes *= memInfo.mem_unit;

    return physical_memory_used_bytes;
#endif
}

// Returns memory bytes free.
//
// https://stackoverflow.com/questions/63166/how-to-determine-cpu-and-memory-consumption-from-inside-a-process/
size_t system_physical_memory_free() {
#ifdef _WIN32  // Windows MSVC
    MEMORYSTATUSEX status;
    status.dwLength = sizeof(status);
    GlobalMemoryStatusEx(&status);

    size_t physical_memory_free_bytes = status.ullAvailPhys;
    return physical_memory_free_bytes;
#else  // Linux and MacOS
    // https://www.man7.org/linux/man-pages/man2/sysinfo.2.html
    struct sysinfo memInfo;
    sysinfo(&memInfo);

    size_t physical_memory_free_bytes = memInfo.freeram;
    // Multiply to avoid int overflow on right hand side.
    physical_memory_free_bytes *= memInfo.mem_unit;

    return physical_memory_free_bytes;
#endif
}

}  // namespace mmmemorysystem
