#include <array>
#include <cstring>

void copyIntoArray(std::array<char, 8>& out, const char* in) {
    out.fill('\0');
    std::strncpy(out.data(), in, out.size() - 1);
}

int main() {
    std::array<char, 8> buffer{};
    copyIntoArray(buffer, "example");
    return 0;
}
