#include <cstdio>
#include <cstring>

int main() {
    char buf[16];
    std::memset(buf, 'x', sizeof buf);
    std::memcpy(buf, "hello", 5); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-16]
    std::puts(buf);
    return 0;
}
