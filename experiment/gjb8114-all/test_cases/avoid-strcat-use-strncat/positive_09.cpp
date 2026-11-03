#include <cstring>

static char* append_bounded(char* dest, const char* src, std::size_t max_chars) {
    return std::strncat(dest, src, max_chars);
}

int main() {
    char buffer[64] = "hello";
    append_bounded(buffer, " world", sizeof(buffer) - std::strlen(buffer) - 1);
    return 0;
}
