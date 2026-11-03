#include <cstring>

struct TextBuffer {
    char contents[64];

    void append(const char* suffix) {
        std::strcat(contents, suffix);  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-5]
    }
};

int main() {
    TextBuffer buffer;
    buffer.contents[0] = '\0';
    buffer.append("xyz");
    return 0;
}
