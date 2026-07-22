#include "tinyxml2.h"
#include "../tinyxml2/tinyxml2.cpp"
#include <iostream>
#include <cstring>

using namespace tinyxml2;

int main()
{
    // 1. Empty string / EOF
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char empty[] = "";
        char* result = doc.Identify(empty, &node, false);
        std::cout << "Branch 1: node=" << (node ? "non-null" : "null") << std::endl;
    }

    // 2. XMLDeclaration (xmlHeader "<?")
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char xmlDecl[] = "<?xml version=\"1.0\"?>";
        char* result = doc.Identify(xmlDecl, &node, false);
        std::cout << "Branch 2: node type=" << (node ? "XMLDeclaration" : "null") << std::endl;
    }

    // 3. XMLComment (commentHeader "<!--")
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char comment[] = "<!-- comment -->";
        char* result = doc.Identify(comment, &node, false);
        std::cout << "Branch 3: node type=" << (node ? "XMLComment" : "null") << std::endl;
    }

    // 4. XMLText CDATA (cdataHeader "<![CDATA[")
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char cdata[] = "<![CDATA[some data]]>";
        char* result = doc.Identify(cdata, &node, false);
        std::cout << "Branch 4: node type=" << (node ? "XMLText (CDATA)" : "null") << std::endl;
    }

    // 5. XMLUnknown DTD (dtdHeader "<!")
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char dtd[] = "<!DOCTYPE html>";
        char* result = doc.Identify(dtd, &node, false);
        std::cout << "Branch 5: node type=" << (node ? "XMLUnknown" : "null") << std::endl;
    }

    // 6. XMLText Pedantic Whitespace (elementHeader "<" with pedantic whitespace)
    {
        XMLDocument doc;
        doc.SetWhitespaceMode(PEDANTIC_WHITESPACE);
        XMLNode* node = nullptr;
        char pedantic[] = "   </tag>";
        char* result = doc.Identify(pedantic, &node, true);
        std::cout << "Branch 6: node type=" << (node ? "XMLText (pedantic)" : "null") << std::endl;
    }

    // 7. XMLElement (elementHeader "<" normal)
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char element[] = "<element>content</element>";
        char* result = doc.Identify(element, &node, false);
        std::cout << "Branch 7: node type=" << (node ? "XMLElement" : "null") << std::endl;
    }

    // 8. XMLText Default (fallback)
    {
        XMLDocument doc;
        XMLNode* node = nullptr;
        char text[] = "plain text content";
        char* result = doc.Identify(text, &node, false);
        std::cout << "Branch 8: node type=" << (node ? "XMLText (default)" : "null") << std::endl;
    }

    return 0;
}