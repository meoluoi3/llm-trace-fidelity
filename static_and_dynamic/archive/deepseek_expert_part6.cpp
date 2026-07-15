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

// Do not use 'using namespace Hjson;' to avoid name collisions.
// Instead, bring in only what's needed and reuse Hjson's existing types.

// The internal enum and classes are likely in the global namespace or an internal
// namespace in the encoder's translation unit. We must match that.
// To avoid ODR violations, we should not redefine types that Hjson already defines
// (like EncoderOptions). We use Hjson::EncoderOptions directly.

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

// Encoder struct uses Hjson::EncoderOptions to avoid ambiguity.
struct Encoder {
  Hjson::EncoderOptions opt;
  std::ostream *os;
  std::locale loc;
  int indent;
  std::regex needsEscape, needsQuotes, needsEscapeML, startsWithKeyword,
    needsEscapeName, lineBreak;
  std::vector<EncodeState> vState;
  std::vector<EncodeParent> vParent;
};

// Provide dummy implementations for the static helper functions to satisfy the linker.
// These are not the focus of the test; they just need to be defined.
static void _quote(Encoder *e, const Hjson::Value &val, const std::string &commentAfter) {
  // Minimal implementation: just output the string representation.
  *e->os << val.to_string();
}

static std::string _quoteForComment(Encoder *e, const std::string &comment) {
  // Minimal implementation: return the comment as-is.
  return comment;
}

// Inline the target function to avoid linker errors, since it is static in the original code.
static void _writeValueBegin(Encoder *e) {
  const Hjson::Value &value = *e->vParent.back().pVal;

  if (e->opt.comments) {
    *e->os << value.get_comment_key();
  }

  switch (value.type()) {
  case Hjson::Type::Double:
    if (std::isnan(static_cast<double>(value)) || std::isinf(static_cast<double>(value))) {
      *e->os << Hjson::Value(Hjson::Type::Null).to_string();
    } else if (!e->opt.allowMinusZero && value == 0 && std::signbit(static_cast<double>(value))) {
      *e->os << Hjson::Value(0).to_string();
    } else {
      *e->os << value.to_string();
    }
    break;

  case Hjson::Type::String:
    _quote(e, value, _quoteForComment(e, value.get_comment_after()));
    break;

  case Hjson::Type::Vector:
    *e->os << "[";
    e->indent++;
    e->vParent.back().commentAfter = value.get_comment_inside();
    e->vState.back() = EncodeState::VectorElemBegin;
    return;

  case Hjson::Type::Map:
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