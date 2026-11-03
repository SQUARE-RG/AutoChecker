#include <array>
#include <cstring>

void copyIntoArray(std::array<char, 16>& out, const char* in) {
    std::strcpy(out.data(), in);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
}

int main() {
    std::array<char, 16> buffer{};
    copyIntoArray(buffer, "text");
    return 0;
}
