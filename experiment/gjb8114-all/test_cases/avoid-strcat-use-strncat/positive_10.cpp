#include <cstddef>
#include <cstring>

extern "C" bool append_c_bounded(char* dest, const char* src, std::size_t available) {
    if (available == 0) {
        return false;
    }
    std::strncat(dest, src, available - 1);
    return true;
}

int main() {
    char buffer[64] = "alpha";
    std::size_t available = sizeof(buffer) - std::strlen(buffer);
    append_c_bounded(buffer, "beta", available);
    return 0;
}
