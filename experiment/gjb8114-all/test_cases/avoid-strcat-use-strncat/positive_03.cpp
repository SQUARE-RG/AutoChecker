#include <cstring>

struct TextBuffer {
    char contents[64];

    void append(const char* suffix) {
        std::strncat(contents, suffix, sizeof(contents) - std::strlen(contents) - 1);
    }
};

int main() {
    TextBuffer buffer;
    buffer.contents[0] = '\0';
    buffer.append("safe");
    return 0;
}
