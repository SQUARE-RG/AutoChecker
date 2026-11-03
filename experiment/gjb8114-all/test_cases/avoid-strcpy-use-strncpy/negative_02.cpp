#include <cstring>

void copy_message(char* destination, const char* source) {
    using std::strcpy;
    strcpy(destination, source); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-4]
}

int main() {
    char buffer[16];
    copy_message(buffer, "hello");
    return buffer[0] == 'h' ? 0 : 1;
}
