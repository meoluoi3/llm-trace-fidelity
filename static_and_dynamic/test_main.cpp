
#include "hjson.h"
#include <iostream>
#include <cmath>
#include <map>
#include <vector>
#include <regex>

using namespace Hjson;

// Forward declarations for internal functions used
namespace Hjson {
    void _quote(Encoder* e, const Value& v, const std::string& commentAfter);
    std::string _quoteForComment(Encoder* e, const std::string& commentAfter);
}

int main() {
    // We need to properly initialize Encoder with all required fields
    Encoder e;
    e.os = &std::cout;
    e.opt.comments = false;
    e.opt.allowMinusZero = false;
    e.opt.omitRootBraces = false;
    e.indent = 0;
    e.loc = std::locale();
    e.needsEscape = std::regex("");
    e.needsQuotes = std::regex("");
    e.needsEscapeML = std::regex("");
    e.startsWithKeyword = std::regex("");
    e.needsEscapeName = std::regex("");
    e.lineBreak = std::regex("");

    // Test Double branch
    {
        Value v(3.14);
        EncodeParent parent(&v);
        e.vParent.clear();
        e.vParent.push_back(parent);
        e.vState.clear();
        e.vState.push_back(EncodeState::ValueBegin);
        _writeValueBegin(&e);
        e.vState.back() = EncodeState::ValueBegin;
    }

    // Test String branch
    {
        Value v("hello");
        EncodeParent parent(&v);
        e.vParent.clear();
        e.vParent.push_back(parent);
        e.vState.clear();
        e.vState.push_back(EncodeState::ValueBegin);
        _writeValueBegin(&e);
        e.vState.back() = EncodeState::ValueBegin;
    }

    // Test Vector branch
    {
        Value v(Type::Vector);
        EncodeParent parent(&v);
        e.vParent.clear();
        e.vParent.push_back(parent);
        e.vState.clear();
        e.vState.push_back(EncodeState::ValueBegin);
        _writeValueBegin(&e);
        e.vState.back() = EncodeState::ValueBegin;
    }

    // Test Map branch
    {
        Value v(Type::Map);
        EncodeParent parent(&v);
        e.vParent.clear();
        e.vParent.push_back(parent);
        e.vState.clear();
        e.vState.push_back(EncodeState::ValueBegin);
        _writeValueBegin(&e);
        e.vState.back() = EncodeState::ValueBegin;
    }

    // Test Default branch (Null)
    {
        Value v(Type::Null);
        EncodeParent parent(&v);
        e.vParent.clear();
        e.vParent.push_back(parent);
        e.vState.clear();
        e.vState.push_back(EncodeState::ValueBegin);
        _writeValueBegin(&e);
        e.vState.back() = EncodeState::ValueBegin;
    }

    return 0;
}
    