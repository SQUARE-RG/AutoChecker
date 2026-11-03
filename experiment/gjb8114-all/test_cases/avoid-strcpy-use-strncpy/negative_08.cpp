#include <cstring>
#include <string>
#include <iostream>

char* duplicateText(const std::string& input) {
    char* buffer = new char[128];
    std::strcpy(buffer, input.c_str()); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    return buffer;
}

int main() {
    std::string value = "heap destination";
    char* result = duplicateText(value);
    std::cout << result << '\n';
    delete[] result;
    return 0;
}
