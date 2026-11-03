#include <cstdlib>
#include <cstring>
#include <iostream>

int main() {
    char* buffer = static_cast<char*>(std::malloc(16));
    if (!buffer) {
        return 1;
    }
    std::strcpy(buffer, "hello");
    char* grown = static_cast<char*>(std::realloc(buffer, 64)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-3]
    if (!grown) {
        std::free(buffer);
        return 1;
    }
    std::strcat(grown, " world");
    std::cout << grown << '\n';
    // 忘记 std::free(grown)，造成泄漏
    return 0;
}
