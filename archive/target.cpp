// target.cpp - toy parser-like function để demo việc trace biến trạng thái
// Biên dịch: g++ -g -O0 -o target target.cpp
#include <iostream>
#include <string>

int classify(const std::string& s) {
    int depth = 0;          // biến trạng thái ta muốn theo dõi
    bool in_quote = false;  // biến trạng thái thứ 2
    int x = 0;

    for (size_t i = 0; i < s.size(); i++) {
        char c = s[i];
        if (c == '"') {
            in_quote = !in_quote;
        } else if (c == '{' && !in_quote) {
            depth++;
        } else if (c == '}' && !in_quote) {
            depth--;
        }
        x = depth * 2 + (in_quote ? 1 : 0);   // dòng "mục tiêu": x phải khớp công thức này
    }
    return x;
}

int main(int argc, char** argv) {
    if (argc < 2) {
        std::cerr << "usage: ./target <input_string>\n";
        return 1;
    }
    int result = classify(argv[1]);
    std::cout << "result=" << result << "\n";
    return 0;
}