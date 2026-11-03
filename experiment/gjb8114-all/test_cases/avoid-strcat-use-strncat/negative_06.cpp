#include <cstring>

template <typename T>
T* append_text(T* dest, const T* src) {
    return std::strcat(dest, src); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
}

int main() {
    char buffer[32] = "Hello";
    const char suffix[] = " world";
    append_text(buffer, suffix);
    return 0;
}
