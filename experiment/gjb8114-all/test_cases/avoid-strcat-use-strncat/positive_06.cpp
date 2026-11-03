#include <cstring>
#include <cstddef>

template <typename T, std::size_t N>
void append_bounded(T (&dest)[N], const T* src) {
    std::size_t used = std::strlen(dest);
    std::strncat(dest, src, N - used - 1);
}

int main() {
    char buffer[32] = "Hello";
    const char suffix[] = " world";
    append_bounded(buffer, suffix);
    return 0;
}
