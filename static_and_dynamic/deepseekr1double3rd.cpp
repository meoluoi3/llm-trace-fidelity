#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>
#include <cmath>
#include <cassert>

using namespace Hjson;

int main() {
    // Create a Value holding NaN to trigger the isnan() branch
    Value val(NAN);

    std::ostringstream oss;
    Encoder e;
    e.os = &oss;
    e.opt.comments = false;          // skip comment output

    e.vParent.emplace_back(&val);    // set current parent value
    e.vState.push_back(EncodeState::ValueBegin);

    _writeValueBegin(&e);            // should output Value(Type::Null).to_string()

    // Verify the expected null output
    assert(oss.str() == Value(Type::Null).to_string());

    return 0;
}