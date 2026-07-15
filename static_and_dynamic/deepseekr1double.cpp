#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>
#include <cassert>
#include <cmath>
#include <map>
#include <string>

using namespace Hjson;

int main() {
    // Create a value of type Double (normal number, not NaN/inf/negative zero)
    Value val(3.14);

    // Set up an Encoder with a stringstream as output
    std::ostringstream oss;
    Encoder e;
    e.os = &oss;
    e.opt.comments = false;          // skip comment output for simplicity
    e.opt.allowMinusZero = true;     // avoid the -0 special case (not strictly needed since val != 0)

    // Push a parent element pointing to our Double value
    e.vParent.emplace_back(&val);
    // Push a dummy state so vState is not empty
    e.vState.push_back(EncodeState::ValueBegin);

    // Call the target function – this will enter the Type::Double branch
    _writeValueBegin(&e);

    // Verify that the output is the string representation of 3.14
    // (Hjson's double-to-string conversion should produce "3.14")
    assert(oss.str() == "3.14");

    // Also verify that the state was advanced to ValueEnd
    assert(e.vState.back() == EncodeState::ValueEnd);

    return 0;
}