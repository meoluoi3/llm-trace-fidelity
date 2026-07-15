#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>
#include <cmath>

using namespace Hjson;

int main() {
    // Create a Double value that is a normal finite number (not NaN, not inf, not -0)
    Value doubleVal(3.14159);

    // Set up an ostringstream to capture output
    std::ostringstream oss;

    // Initialize the Encoder
    Encoder e;
    e.os = &oss;
    e.opt.comments = false;
    e.opt.allowMinusZero = true;
    e.indent = 0;

    // Push a parent that references the double value
    e.vParent.emplace_back(&doubleVal);
    // Ensure vState has at least one element for the function to modify
    e.vState.push_back(EncodeState::ValueBegin);

    // Call the target function
    _writeValueBegin(&e);

    // Output the result for verification
    std::cout << oss.str() << std::endl;

    return 0;
}