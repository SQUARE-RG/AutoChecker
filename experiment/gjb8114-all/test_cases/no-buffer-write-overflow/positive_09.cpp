#include <cstring>

int main() {
    char dst[4] = {0};
    const char* src = "abc";
    std::strncpy(dst, src, sizeof(dst));
    return 0;
}
