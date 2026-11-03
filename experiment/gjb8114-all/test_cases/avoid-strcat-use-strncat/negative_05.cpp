#include <cstring>

int main() {
    char buffer[32] = "Hello";
    const char suffix[] = " world";

    auto append = [](char* dest, const char* src) {
        return std::strcat(dest, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
    };

    append(buffer, suffix);
    return 0;
}
