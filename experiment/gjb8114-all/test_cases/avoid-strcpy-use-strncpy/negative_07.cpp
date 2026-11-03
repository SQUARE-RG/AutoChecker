#include <cstring>
#include <string>
#include <iostream>

int main() {
    char target[32] = {};
    std::string input = "runtime source";

    auto copyInput = [&target](const char* source) {
        std::strcpy(target, source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    };

    copyInput(input.c_str());
    std::cout << target << '\n';
    return 0;
}
