#include "hjson.h"
#include "../hjson-cpp/src/hjson_encode.cpp"
#include <iostream>
#include <locale>
#include <regex>
#include <sstream>
using namespace Hjson;

int main() {
    Encoder e;
    e.opt.comments = false;
    e.opt.allowMinusZero = true;
    e.opt.omitRootBraces = false;
    e.indent = 0;
    e.loc = std::locale();
    std::ostringstream oss;
    e.os = &oss;

    e.needsEscape = std::regex("[\x00-\x1f\x7f-\x9f\\\\\"]");
    e.needsQuotes = std::regex("^$|[\\x00-\\x20\\x7f-\\x9f#\\{\\}/\\\\\\s,:\\[\\]]");
    e.needsEscapeML = std::regex("'''");
    e.startsWithKeyword = std::regex("^(true|false|null)\\s*:");
    e.needsEscapeName = std::regex("[,\\{\\}\\[\\]\\s#\"]");
    e.lineBreak = std::regex("\\r\\n|\\n|\\r");

    Value val(42);
    EncodeParent parent(&val);
    parent.pVal = &val;
    parent.index = 0;
    parent.isEmpty = false;

    e.vParent.push_back(parent);
    e.vState.push_back(EncodeState::ValueBegin);

    _writeValueBegin(&e);

    return 0;
}