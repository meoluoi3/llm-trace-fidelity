#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <cmath>
#include <limits>

using namespace Hjson;

int main() {
    Encoder e;
    std::ostringstream oss;
    e.os = &oss;
    e.opt.comments = false;
    e.opt.allowMinusZero = true;
    e.indent = 0;

    Value val(-0.0);
    
    EncodeParent parent(&val);
    parent.index = 0;
    parent.isEmpty = false;
    e.vParent.push_back(parent);
    
    e.vState.push_back(EncodeState::ValueBegin);
    
    _writeValueBegin(&e);
    
    std::string result = oss.str();
    bool branchHit = (result == "0");
    
    if (branchHit) {
        std::cout << "SUCCESS: Target branch executed. Output: " << result << std::endl;
        return 0;
    } else {
        std::cout << "FAIL: Target branch not executed. Output: " << result << std::endl;
        return 1;
    }
}