#include <cstring>

int main() {
    char destination[32];
    const char* source = "hello";
    std::strcpy(destination, source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
    return destination[0] == 'h' ? 0 : 1;
}
