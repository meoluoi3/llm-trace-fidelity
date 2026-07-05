#include "hjson.h"
#include <iostream>

int main(int argc, char** argv) {
  if (argc < 2) {
    std::cerr << "usage: ./target '<json_string>'\n";
    return 1;
  }
  
  try {
    // 1. Unmarshal: Đọc chuỗi JSON/HJSON từ terminal biến thành C++ Object
    Hjson::Value v = Hjson::Unmarshal(argv[1]);
    
    // 2. Marshal: Ghi Object đó ra lại chuỗi (Thao tác này sẽ gọi ngầm _writeValueBegin)
    std::cout << Hjson::Marshal(v) << "\n";
  } catch (const std::exception& e) {
    std::cerr << "Parse error: " << e.what() << "\n";
    return 1;
  }
  
  return 0;
}