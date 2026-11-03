#include <iostream>
#include <string>
#include <vector>

int main() {
    int intValue = 42;
    std::string stringValue = "hello";

    std::vector<void*> container; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-3-2]
    container.push_back(&intValue);
    container.push_back(&stringValue);

    int* intPtr = static_cast<int*>(container[0]);
    std::string* stringPtr = static_cast<std::string*>(container[1]);

    std::cout << *intPtr << " " << *stringPtr << std::endl;
    return 0;
}
