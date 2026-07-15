#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>
#include <cmath>

using namespace Hjson;

int main() {
    // Create a Value of type Double containing negative zero.
    double neg_zero = -0.0;
    Value val(neg_zero);

    // Set up the Encoder with output stream and required options.
    std::ostringstream oss;
    Encoder e;
    e.os = &oss;
    e.opt.allowMinusZero = false;  // trigger the special branch
    e.opt.comments = false;

    // Push the parent element so vParent.back() returns a reference to our value.
    e.vParent.emplace_back(&val);
    // Push a dummy state so vState is not empty.
    e.vState.push_back(EncodeState::ValueBegin);

    // Call the function. It should enter case Type::Double,
    // skip the NaN/Inf branch, then hit:
    //   else if (!e->opt.allowMinusZero && value == 0 && std::signbit(...))
    // and output Value(0).to_string().
    _writeValueBegin(&e);

    // (Optional) verify that the output matches Value(0).to_string().
    // assert(oss.str() == Value(0).to_string());

    return 0;
}