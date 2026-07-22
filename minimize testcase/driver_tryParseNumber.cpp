#include "hjson.h"
#include "../hjson-cpp/src/hjson_parsenumber.cpp"
#include <iostream>
#include <string>
#include <cstring>

using namespace Hjson;

int main() {
    Value val;
    bool result;

    // Test 1: Valid integer
    std::cout << "Test 1 (valid integer '123'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 2: Valid negative integer
    std::cout << "Test 2 (valid negative integer '-456'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 3: Valid float
    result = tryParseNumber(&val, "3.14", 4, false);
    std::cout << "Test 3 (valid float '3.14'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 4: Valid scientific notation with 'e'
    result = tryParseNumber(&val, "1e5", 3, false);
    std::cout << "Test 4 (valid scientific '1e5'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 5: Valid scientific notation with 'E' and '+'
    result = tryParseNumber(&val, "2.5E+3", 6, false);
    std::cout << "Test 5 (valid scientific '2.5E+3'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 6: Valid scientific notation with 'e' and '-'
    result = tryParseNumber(&val, "4.7e-2", 6, false);
    std::cout << "Test 6 (valid scientific '4.7e-2'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 7: Single zero
    result = tryParseNumber(&val, "0", 1, false);
    std::cout << "Test 7 (single zero '0'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 8: Leading zeros (invalid)
    result = tryParseNumber(&val, "00123", 5, false);
    std::cout << "Test 8 (leading zeros '00123'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 9: Number with trailing space
    result = tryParseNumber(&val, "42   ", 5, false);
    std::cout << "Test 9 (number with trailing space '42   '): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 10: Negative zero
    result = tryParseNumber(&val, "-0", 2, false);
    std::cout << "Test 10 (negative zero '-0'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 11: Decimal starting with dot? Actually needs digit before dot based on parser
    result = tryParseNumber(&val, "0.5", 3, false);
    std::cout << "Test 11 (valid decimal '0.5'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 12: stopAtNext with comma
    result = tryParseNumber(&val, "123,", 4, true);
    std::cout << "Test 12 (stopAtNext with comma '123,'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 13: stopAtNext with brace
    result = tryParseNumber(&val, "456}", 4, true);
    std::cout << "Test 13 (stopAtNext with brace '456}'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 14: stopAtNext with bracket
    result = tryParseNumber(&val, "789]", 4, true);
    std::cout << "Test 14 (stopAtNext with bracket '789]'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 15: stopAtNext with hash
    result = tryParseNumber(&val, "10#", 3, true);
    std::cout << "Test 15 (stopAtNext with hash '10#'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 16: stopAtNext with line comment
    result = tryParseNumber(&val, "20//comment", 11, true);
    std::cout << "Test 16 (stopAtNext with line comment '20//comment'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 17: stopAtNext with block comment
    result = tryParseNumber(&val, "30/*comment*/", 13, true);
    std::cout << "Test 17 (stopAtNext with block comment '30/*comment*/'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 18: Invalid - no digits after minus
    result = tryParseNumber(&val, "-", 1, false);
    std::cout << "Test 18 (invalid '-'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 19: Invalid - just a dot
    result = tryParseNumber(&val, ".", 1, false);
    std::cout << "Test 19 (invalid '.'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 20: Empty input
    result = tryParseNumber(&val, "", 0, false);
    std::cout << "Test 20 (empty input): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 21: Valid negative float
    result = tryParseNumber(&val, "-1.23", 5, false);
    std::cout << "Test 21 (valid negative float '-1.23'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 22: Multiple leading zeros in decimal
    result = tryParseNumber(&val, "00.5", 4, false);
    std::cout << "Test 22 (leading zeros in decimal '00.5'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 23: Scientific notation without digits after 'e'
    result = tryParseNumber(&val, "1e", 2, false);
    std::cout << "Test 23 (invalid '1e'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 24: Negative zero with decimal
    result = tryParseNumber(&val, "-0.0", 4, false);
    std::cout << "Test 24 (negative zero decimal '-0.0'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 25: Number with tab and newline whitespace
    result = tryParseNumber(&val, "99\t\n ", 5, false);
    std::cout << "Test 25 (number with whitespace '99\\t\\n '): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 26: stopAtNext disabled, invalid char remains
    result = tryParseNumber(&val, "100a", 4, false);
    std::cout << "Test 26 (invalid trailing char '100a'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 27: Valid number with 'e' and no sign
    result = tryParseNumber(&val, "5e3", 3, false);
    std::cout << "Test 27 (valid '5e3'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 28: stopAtNext with slash but not comment (not followed by / or *)
    result = tryParseNumber(&val, "50/", 3, true);
    std::cout << "Test 28 (stopAtNext with '50/' not comment): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 29: Invalid with letter after number (not stopAtNext)
    result = tryParseNumber(&val, "7x", 2, false);
    std::cout << "Test 29 (invalid '7x'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 30: Valid large integer
    result = tryParseNumber(&val, "999999999", 9, false);
    std::cout << "Test 30 (valid large integer '999999999'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 31: Scientific with capital E and minus
    result = tryParseNumber(&val, "1E-10", 5, false);
    std::cout << "Test 31 (valid '1E-10'): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 32: Only minus and dot
    result = tryParseNumber(&val, "-.", 2, false);
    std::cout << "Test 32 (invalid '-.'): " << (result ? "FAIL" : "PASS") << std::endl;

    // Test 33: Number with only whitespace after stopAtNext
    result = tryParseNumber(&val, "42   ", 5, true);
    std::cout << "Test 33 (number with whitespace stopAtNext '42   '): " << (result ? "PASS" : "FAIL") << std::endl;

    // Test 34: stopAtNext false with valid char after whitespace
    result = tryParseNumber(&val, "17  #", 5, false);
    std::cout << "Test 34 (invalid '17  #' stopAtNext=false): " << (result ? "FAIL" : "PASS") << std::endl;

    return 0;
}