#include <cstring>

struct Buffer {
    char data[64] = "header";

    Buffer& operator+=(const char* tag) {
        std::strcat(data, tag);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
        return *this;
    }
};

int main() {
    Buffer buffer;
    buffer += "!";
    return 0;
}
