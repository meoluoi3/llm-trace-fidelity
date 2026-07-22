#include "hjson.h"
#include "../hjson-cpp/src/hjson_parsenumber.cpp"
#include <iostream>
#include <cstring>
using namespace Hjson;

int main() {
    Value val;
    // 1. Valid integer
    tryParseNumber(&val, "42", 2, false);
    // 2. Valid negative integer
    tryParseNumber(&val, "-17", 3, false);
    // 3. Valid float with decimal
    tryParseNumber(&val, "3.14", 4, false);
    // 4. Valid float with exponent
    tryParseNumber(&val, "1e10", 4, false);
    // 5. Valid float with negative exponent
    tryParseNumber(&val, "2.5E-3", 6, false);
    // 6. Valid float with plus exponent
    tryParseNumber(&val, "9E+2", 4, false);
    // 7. Leading zeros (invalid)
    tryParseNumber(&val, "007", 3, false);
    // 8. Single zero (valid)
    tryParseNumber(&val, "0", 1, false);
    // 9. Trailing whitespace accepted
    tryParseNumber(&val, "123 ", 4, false);
    // 10. stopAtNext with comma
    tryParseNumber(&val, "456,", 4, true);
    // 11. stopAtNext with brace
    tryParseNumber(&val, "789}", 4, true);
    // 12. stopAtNext with bracket
    tryParseNumber(&val, "101]", 4, true);
    // 13. stopAtNext with hash comment
    tryParseNumber(&val, "202#", 4, true);
    // 14. stopAtNext with // comment
    tryParseNumber(&val, "303//", 5, true);
    // 15. stopAtNext with /* comment
    tryParseNumber(&val, "404/*", 5, true);
    // 16. Invalid character after number
    tryParseNumber(&val, "505x", 4, false);
    // 17. Negative zero (valid)
    tryParseNumber(&val, "-0", 2, false);
    // 18. Float starting with dot (should be invalid by _parseFloat)
    tryParseNumber(&val, ".5", 2, false);
    // 19. Empty string
    tryParseNumber(&val, "", 0, false);
    // 20. Just a minus sign
    tryParseNumber(&val, "-", 1, false);
    // 21. Number with leading zeros and decimal
    tryParseNumber(&val, "00.5", 4, false);
    // 22. stopAtNext without matching punctuator
    tryParseNumber(&val, "99:", 3, true);
    // 23. Valid number at exact end of buffer
    tryParseNumber(&val, "7", 1, false);
    // 24. Exponent with no digits after
    tryParseNumber(&val, "5e", 2, false);
    // 25. Exponent sign with no digits after
    tryParseNumber(&val, "5e-", 3, false);
    // 26. Valid number with trailing newline
    tryParseNumber(&val, "88\n", 3, false);
    return 0;
}