#include <array>
#include <cstddef>
#include <cstring>

template <std::size_t N>
void copy_text(std::array<char, N>& destination, const char* source) {
    static_assert(N > 0, "destination must have space");
    std::strncpy(destination.data(), source, N - 1);
    destination[N - 1] = '\0';
}

int main() {
    std::array<char, 8> text{};
    copy_text(text, "alpha");
    return text[0] == 'a' ? 0 : 1;
}
