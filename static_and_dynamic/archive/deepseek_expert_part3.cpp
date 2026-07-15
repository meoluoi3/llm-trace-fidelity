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

// Bring the required internal symbols into scope.
// These are not in the public Hjson namespace, they are internal to the encoder.
// Based on the context, they are defined at global scope (or in an internal namespace).
// We redeclare them here so the test can compile and link against the encoder's object files.
enum class EncodeState {
  ValueBegin,
  ValueEnd,
  VectorElemBegin,
  MapElemBegin,
};

class EncodeParent {
public:
  EncodeParent(const Hjson::Value *_pVal) : pVal(_pVal), index(0), isEmpty(true) {}
  const Hjson::Value *pVal;
  int index;
  bool isEmpty;
  std::string commentAfter;
  std::map<std::string, Hjson::Value>::const_iterator it;
};

struct EncoderOptions {
  bool comments = false;
  bool allowMinusZero = true;
  bool omitRootBraces = false;
  // Add other options as needed, these are the only ones used.
};

struct Encoder {
  EncoderOptions opt;
  std::ostream *os;
  std::locale loc;
  int indent;
  std::regex needsEscape, needsQuotes, needsEscapeML, startsWithKeyword,
    needsEscapeName, lineBreak;
  std::vector<EncodeState> vState;
  std::vector<EncodeParent> vParent;
};

// Declare the target function (defined as static in the encoder translation unit,
// but we link against that unit).
void _writeValueBegin(Encoder *e);

// Declare helper functions used by the target function (also static in the encoder unit).
void _quote(Encoder *e, const Hjson::Value &val, const std::string &commentAfter);
std::string _quoteForComment(Encoder *e, const std::string &comment);

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
        Hjson::Value val(3.14);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (NaN)
    {
        double nan_val = std::numeric_limits<double>::quiet_NaN();
        Hjson::Value val(nan_val);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (inf)
    {
        double inf_val = std::numeric_limits<double>::infinity();
        Hjson::Value val(inf_val);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Double (minus zero)
    {
        e.opt.allowMinusZero = false;
        double neg_zero = -0.0;
        Hjson::Value val(neg_zero);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
        e.opt.allowMinusZero = true;
    }

    // Test case Type::String
    {
        Hjson::Value val(std::string("test string"));
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    // Test case Type::Vector
    {
        Hjson::Value val(Hjson::Type::Vector);
        val.push_back(Hjson::Value(1));
        val.push_back(Hjson::Value(2));
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    e.vState.back() = EncodeState::ValueBegin;

    // Test case Type::Map
    {
        Hjson::Value val(Hjson::Type::Map);
        val["key"] = Hjson::Value("value");
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    e.vState.back() = EncodeState::ValueBegin;

    // Test case default (Type::Int)
    {
        Hjson::Value val(42);
        e.vParent.back().pVal = &val;
        e.vState.back() = EncodeState::ValueBegin;
        _writeValueBegin(&e);
    }

    return 0;
}