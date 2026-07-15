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

// Redeclare internal encoder types exactly as they appear in the encoder's translation unit.
enum class EncodeState {
  ValueBegin,
  ValueEnd,
  VectorElemBegin,
  MapElemBegin,
};

class EncodeParent {
public:
  EncodeParent(const Value *_pVal) : pVal(_pVal), index(0), isEmpty(true) {}
  const Value *pVal;
  int index;
  bool isEmpty;
  std::string commentAfter;
  std::map<std::string, Value>::const_iterator it;
};

struct EncoderOptions {
  bool comments = false;
  bool allowMinusZero = true;
  bool omitRootBraces = false;
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

// Declare helper functions (defined static in the encoder TU).
void _quote(Encoder *e, const Value &val, const std::string &commentAfter);
std::string _quoteForComment(Encoder *e, const std::string &comment);

// Inline the target function to avoid linker errors, since it is static in the original code.
static void _writeValueBegin(Encoder *e) {
  const Value &value = *e->vParent.back().pVal;

  if (e->opt.comments) {
    *e->os << value.get_comment_key();
  }

  switch (value.type()) {
  case Type::Double:
    if (std::isnan(static_cast<double>(value)) || std::isinf(static_cast<double>(value))) {
      *e->os << Value(Type::Null).to_string();
    } else if (!e->opt.allowMinusZero && value == 0 && std::signbit(static_cast<double>(value))) {
      *e->os << Value(0).to_string();
    } else {
      *e->os << value.to_string();
    }
    break;

  case Type::String:
    _quote(e, value, _quoteForComment(e, value.get_comment_after()));
    break;

  case Type::Vector:
    *e->os << "[";
    e->indent++;
    e->vParent.back().commentAfter = value.get_comment_inside();
    e->vState.back() = EncodeState::VectorElemBegin;
    return;

  case Type::Map:
    if (!e->opt.omitRootBraces || e->vParent.size() > 1 || value.empty()) {
      *e->os << "{";
      e->indent++;
    }
    e->vParent.back().commentAfter = value.get_comment_inside();
    e->vParent.back().it = value.begin();
    e->vState.back() = EncodeState::MapElemBegin;
    return;

  default:
    *e->os << value.to_string();
  }

  e->vState.back() = EncodeState::ValueEnd;
}

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