#include <cstring>

int main() {
    char message[64] = "hello";
    const char* suffix = " world";
    std::strcat(message, suffix); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
    return 0;
}
