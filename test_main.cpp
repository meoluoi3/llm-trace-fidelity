// test_main.cpp - driver to exercise Hjson::_writeValueBegin via Hjson::Marshal
//
// Unlike target.cpp for classify() (input = a text string), _writeValueBegin
// does not take text as input -- it takes an in-memory Hjson::Value (map,
// vector, number, string...). So instead of passing a string on the command
// line, we pick WHICH Value to build via a "mode" argument, then let
// Hjson::Marshal() call _writeValueBegin() internally.
//
// Build (run from inside a cloned hjson-cpp checkout, this file placed at
// the repo root, next to the src/ and include/ folders):
//   git clone --depth 1 https://github.com/hjson/hjson-cpp.git
//   cd hjson-cpp
//   cp /path/to/test_main.cpp .
//   g++ -g -O0 -std=c++11 -Iinclude/hjson test_main.cpp src/*.cpp -o target
//
// -O0 is mandatory, same reason as before: optimization reorders/removes
// lines and variables, which would corrupt the ground-truth trace.
//
// Usage: ./target <mode>
//   vector   -> exercises "case Type::Vector"
//   map      -> exercises "case Type::Map"
//   nan      -> exercises the NaN branch (std::isnan check)
//   negzero  -> exercises the "-0.0" branch (signbit check)
//   string   -> exercises "case Type::String"

#include "hjson.h"
#include <iostream>
#include <limits>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: ./target <vector|map|nan|negzero|string>\n";
    return 1;
  }
  std::string mode = argv[1];
  Hjson::Value v;

  if (mode == "vector") {
    v = Hjson::Value(Hjson::Type::Vector);
    v.push_back(1);
    v.push_back(2);
    v.push_back(3);
  } else if (mode == "map") {
    v = Hjson::Value(Hjson::Type::Map);
    v["a"] = 1;
  } else if (mode == "nan") {
    v = std::numeric_limits<double>::quiet_NaN();
  } else if (mode == "negzero") {
    v = -0.0;
  } else if (mode == "string") {
    v = "hello";
  } else {
    std::cerr << "unknown mode: " << mode << "\n";
    return 1;
  }

  std::cout << Hjson::Marshal(v) << "\n";
  return 0;
}