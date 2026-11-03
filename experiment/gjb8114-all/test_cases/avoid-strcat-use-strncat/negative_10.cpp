#include <cstring>

extern "C" void append_c(char* dest, const char* src) {
    std::strcat(dest, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
}

int main() {
    char buffer[64] = "alpha";
    append_c(buffer, "beta");
    return 0;
}
