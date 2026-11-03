#include <cstring>
#include <cstddef>

int main() {
    char buffer[32] = "Hello";
    const char suffix[] = " world";

    auto append = [](char* dest, std::size_t dest_size, const char* src) {
        std::size_t used = std::strlen(dest);
        if (used < dest_size) {
            std::strncat(dest, src, dest_size - used - 1);
        }
    };

    append(buffer, sizeof(buffer), suffix);
    return 0;
}
