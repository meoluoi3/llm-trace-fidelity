#include <iostream>
#include <cmath>
#include <map>
#include <string>
#include <sstream>
#include <vector>
#include <regex>
#include <locale>
#include <limits>

#include "hjson.h"

using namespace Hjson;

int main() {
    Encoder e;
    std::ostringstream oss;
    e.os = &oss;
    e.loc = std::locale::classic();
    e.indent = 0;
    e.opt.comments = false;
    e.opt.allowMinusZero = true;
    e.opt.omitRootBraces = false;

    e.vState.push_back(EncodeState::ValueBegin);
    e.vParent.emplace_back(nullptr);

    // Test case Type::Double (normal)
    {
        Value val(3.14);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (NaN)
    {
        double nan_val = std::numeric_limits<double>::quiet_NaN();
        Value val(nan_val);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (inf)
    {
        double inf_val = std::numeric_limits<double>::infinity();
        Value val(inf_val);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (minus zero)
    {
        e.opt.allowMinusZero = false;
        double neg_zero = -0.0;
        Value val(neg_zero);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
        e.opt.allowMinusZero = true;
    }

    // Test case Type::String
    {
        Value val(std::string("test string"));
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Vector
    {
        Value val(Type::Vector);
        val.push_back(Value(1));
        val.push_back(Value(2));
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    e.vState.back() = EncodeState::ValueBegin;

    // Test case Type::Map
    {
        Value val(Type::Map);
        val["key"] = Value("value");
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    e.vState.back() = EncodeState::ValueBegin;

    // Test case default (Type::Int)
    {
        Value val(42);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    return 0;
}