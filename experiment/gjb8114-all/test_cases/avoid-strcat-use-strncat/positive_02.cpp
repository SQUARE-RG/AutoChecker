#include <cstddef>
#include <cstring>

void append_bounded(char* dest, const char* src, std::size_t dest_size) {
    std::size_t used = std::strlen(dest);
    if (used < dest_size) {
        std::strncat(dest, src, dest_size - used - 1);
    }
}

int main() {
    char path[32] = "/tmp";
    append_bounded(path, "/log", sizeof(path));
    return 0;
}
