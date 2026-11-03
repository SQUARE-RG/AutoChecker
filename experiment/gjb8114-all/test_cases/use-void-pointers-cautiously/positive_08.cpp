#include <iostream>
#include <map>
#include <string>

int main() {
    int intValue = 100;
    std::string stringValue = "world";

    std::map<std::string, int*> intRegistry;
    std::map<std::string, std::string*> stringRegistry;

    intRegistry["integer"] = &intValue;
    stringRegistry["string"] = &stringValue;

    int* intPtr = intRegistry.at("integer");
    std::string* stringPtr = stringRegistry.at("string");

    std::cout << *intPtr << " " << *stringPtr << std::endl;
    return 0;
}
