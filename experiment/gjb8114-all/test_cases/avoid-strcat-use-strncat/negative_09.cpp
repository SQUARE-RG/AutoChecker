#include <cstring>

static char* append_text(char* dest, const char* src) {
    return std::strcat(dest, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
}

int main() {
    char buffer[64] = "hello";
    append_text(buffer, " world");
    return 0;
}
