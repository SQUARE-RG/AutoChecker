#include <cstring>

int main() {
    char dst[4] = {0};
    const char* src = "abcdef";
    std::strncpy(dst, src, 6);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
