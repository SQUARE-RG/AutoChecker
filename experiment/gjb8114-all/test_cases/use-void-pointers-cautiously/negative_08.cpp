#include <iostream>
#include <map>
#include <string>

int main() {
    int intValue = 100;
    std::string stringValue = "world";

    std::map<std::string, void*> registry; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    registry["integer"] = &intValue;
    registry["string"] = &stringValue;

    int* intPtr = static_cast<int*>(registry["integer"]);
    std::string* stringPtr = static_cast<std::string*>(registry["string"]);

    std::cout << *intPtr << " " << *stringPtr << std::endl;
    return 0;
}
