#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>

using namespace Hjson;

int main() {
    Value value(-0.0);

    std::ostringstream oss;

    Encoder encoder;
    encoder.os = &oss;
    encoder.indent = 0;

    encoder.opt.comments = false;
    encoder.opt.allowMinusZero = false;
    encoder.opt.omitRootBraces = false;

    encoder.vParent.emplace_back(&value);
    encoder.vState.emplace_back(EncodeState::ValueBegin);

    _writeValueBegin(&encoder);

    return 0;
}