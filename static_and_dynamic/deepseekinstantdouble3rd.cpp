#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <cmath>
using namespace Hjson;

int main() {
    Encoder e;
    e.opt.comments = false;
    e.opt.allowMinusZero = true;
    e.os = new std::ostringstream();
    e.indent = 0;
    
    Value v(std::nan(""));
    EncodeParent parent(&v);
    e.vParent.push_back(parent);
    e.vState.push_back(EncodeState::ValueBegin);
    
    _writeValueBegin(&e);
    
    delete e.os;
    return 0;
}