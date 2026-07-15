#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <sstream>
#include <vector>

using namespace Hjson;

int main() {
    Value value(3.141592653589793);

    std::ostringstream oss;

    Encoder encoder;
    encoder.os = &oss;
    encoder.indent = 0;

    encoder.opt.comments = false;
    encoder.opt.allowMinusZero = true;
    encoder.opt.omitRootBraces = false;

    encoder.vParent.emplace_back(&value);
    encoder.vState.emplace_back(EncodeState::ValueBegin);

    _writeValueBegin(&encoder);

    return 0;
}