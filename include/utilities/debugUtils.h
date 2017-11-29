/*! Debugging Utils - printing and benchmarking.
 */

#ifndef DEBUG_UTILS_H
#define DEBUG_UTILS_H

// STL
#include <iostream> // cout, cerr, endl
#include <iomanip>  // setfill, setw
#include <string>   // string

// Linux Specific Functions
#include <sys/time.h>  // gettimeofday
#include <sys/types.h> // uint32_t, uint64_t, etc

// Debug defines...
//#ifndef NDEBUG
//#  define DBG(x)
//#else
#define DBG(x) do { std::cerr << __FILE__  << ':' << __LINE__ << ' ' << x << std::endl; } while (0)
//#endif // NDEBUG

#define VRB(x) do { if (verbose) { std::cout << x << std::endl; } } while (0)
#define ERR(x) do { std::cerr << "ERROR: " << x << std::endl; } while (0)
#define WRN(x) do { std::cerr << "WARNING: " << x << std::endl; } while (0)
#define INFO(x) do { std::cout << x << std::endl; } while (0)


namespace debug {
    typedef unsigned int uint32;
    typedef unsigned long long uint64;
    typedef unsigned long long Ticks;

    // Measuring CPU Clock-Cycles on Windows or Linux.
    // http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
#ifdef _WIN32
    //  Windows
#include <intrin.h>
  uint64_t rdtsc(){
      return __rdtsc();
  }

#else

    //  Linux/GCC
    static inline
    uint64 rdtsc() {
        uint32 lo, hi;
        __asm__ __volatile__ ("rdtsc" : "=a" (lo), "=d" (hi));
        return ((uint64) hi << 32) | lo;
    }

#endif


    // Get time of day with high accuracy.
    //
    // http://stackoverflow.com/questions/1861294/how-to-calculate-execution-time-of-a-code-snippet-in-cw
    typedef unsigned long long Timestamp;

    // Get the current time - used for profiling and debug.
    inline
    Timestamp get_timestamp() {
        struct timeval now;
        gettimeofday(&now, NULL);
        return now.tv_usec + (Timestamp) now.tv_sec * 1000000;
    }

    // CPU Clock-cycle timing.
    //
    // Article1: http://lemire.me/blog/2012/06/20/do-not-waste-time-with-stl-vectors/
    // Article2: http://stackoverflow.com/questions/13772567/get-cpu-cycle-count
    // Code: https://github.com/lemire/Code-used-on-Daniel-Lemire-s-blog/blob/master/2012/06/20/testvector.cpp
    //
    //
    // Example Code Start:
    //   CPUBenchmark time;
    //   const size_t N = 100 * 1000 * 1000 ;
    //   time.start();
    //   std::cout.precision(3);
    //   std::cout << " report speed in CPU cycles per integer" << std::endl;
    //   std::cout << std::endl << "ignore this:" << runtestnice(N) << std::endl;
    //   std::cout << "with push_back:"<<(time.stop()*1.0/N)<<std::endl;
    // Example Code End:
    //

    // Wrapper class around assembly clock cycle timer.
    class CPUBenchmark {
    public:
        CPUBenchmark() :
                ticktime(0),
                ticktimeTotal(0){
            start();
        }

        Ticks ticktime;
        Ticks ticktimeTotal;

        void start() {
            ticktime = rdtsc();
        }

        Ticks stop() {
            return ticktimeTotal += rdtsc() - ticktime;
        }

        void print(std::string heading, uint loopNums = 0) {
            Ticks ticks = ticktimeTotal;
            if (loopNums <= 1) {
                std::cout << heading << " Ticks: ";
            } else if (loopNums > 0) {
                ticks /= loopNums;
                std::cout << heading << " Ticks (per-loop): ";
            }
            std::cout << ticks << " ticks";
            std::cout << std::endl;
        }
    };


    // Wrapper class around 'get_timestamp' timer.
    class TimestampBenchmark {
    public:
        TimestampBenchmark() :
                timestamp(0),
                timestampTotal(0) {
            start();
        }

        Timestamp timestamp;
        Timestamp timestampTotal;

        void start() {
            timestamp = get_timestamp();
        }

        Timestamp stop() {
            return timestampTotal += get_timestamp() - timestamp;
        }

        void print(std::string heading, uint loopNums = 0) {
            return printInSec(heading, loopNums);
        }

        void printInSec(std::string heading, uint loopNums = 0) {
            double secs = (double) (timestampTotal / 1000000.0L);
            if (loopNums <= 1) {
                std::cout << heading << " Time: ";
            } else if (loopNums > 0) {
                secs /= loopNums;
                std::cout << heading << " Time (per-loop): ";
            }
            std::cout << secs << " seconds";
            std::cout << std::endl;
        }

    };

//    inline
//    void printLineOut(std::string str = "-", int num = 80) {
//        char c = '-'; // TODO: Get this value from 'str'.
//        std::cout << std::setfill(c) << std::setw(num) << str << std::endl;
//    }
//
//    inline
//    void printLineErr(std::string str = "-", int num = 80) {
//        char c = '-'; // TODO: Get this value from 'str'.
//        std::cerr << std::setfill(c) << std::setw(num) << str << std::endl;
//    }

}

#endif // DEBUG_UTILS_H
