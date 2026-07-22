#include "tinyxml2.h"
#include "../tinyxml2/tinyxml2.cpp"
#include <iostream>
#include <cstring>
using namespace tinyxml2;

int main() {
    XMLDocument doc;
    XMLNode* node = nullptr;

    // 1. Empty string / EOF
    {
        XMLDocument doc1;
        XMLNode* n1 = nullptr;
        char p1[] = "";
        doc1.Identify(p1, &n1, false);
    }

    // 2. XMLDeclaration
    {
        XMLDocument doc2;
        XMLNode* n2 = nullptr;
        char p2[] = "<?xml version=\"1.0\"?>";
        doc2.Identify(p2, &n2, false);
    }

    // 3. XMLComment
    {
        XMLDocument doc3;
        XMLNode* n3 = nullptr;
        char p3[] = "<!-- comment -->";
        doc3.Identify(p3, &n3, false);
    }

    // 4. XMLText CDATA
    {
        XMLDocument doc4;
        XMLNode* n4 = nullptr;
        char p4[] = "<![CDATA[ data ]]>";
        doc4.Identify(p4, &n4, false);
    }

    // 5. XMLUnknown DTD
    {
        XMLDocument doc5;
        XMLNode* n5 = nullptr;
        char p5[] = "<!DOCTYPE html>";
        doc5.Identify(p5, &n5, false);
    }

    // 6. XMLText Pedantic Whitespace
    {
        XMLDocument doc6;
        XMLNode* n6 = nullptr;
        char p6[] = " </>";
        doc6.SetWhitespaceMode(PEDANTIC_WHITESPACE);
        doc6.Identify(p6, &n6, true);
    }

    // 7. XMLElement
    {
        XMLDocument doc7;
        XMLNode* n7 = nullptr;
        char p7[] = "<element>";
        doc7.Identify(p7, &n7, false);
    }

    // 8. XMLText Default fallback
    {
        XMLDocument doc8;
        XMLNode* n8 = nullptr;
        char p8[] = "plain text";
        doc8.Identify(p8, &n8, false);
    }

    return 0;
}