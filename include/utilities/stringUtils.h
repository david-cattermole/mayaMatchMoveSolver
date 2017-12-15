/*! Generic string helper functions.
 */

#ifndef STRING_UTILS_H
#define STRING_UTILS_H

// #include <cstdio>   // FILE, fwrite, fopen
#include <sstream>  // stringstream
#include <cmath>    // fabs

namespace string {

    /*! Convert a number to a string
     *
     * @tparam NUM_TYPE
     * @param num
     * @return
     */
    template<typename NUM_TYPE>
    inline
    std::string numberToString(NUM_TYPE num) {
        std::stringstream ss;
        ss << num;
        return ss.str();
    }

    /*! Convert a string to a number.
     *
     * @tparam NUM_TYPE
     * @param text
     * @return
     */
    template<typename NUM_TYPE>
    inline
    NUM_TYPE stringToNumber(const std::string &text) {
        std::stringstream ss(text);
        NUM_TYPE result;
        ss >> result;
        if (!result) {
            result = 0;
        }
        return result;
    }

}

#endif // STRING_UTILS_H
