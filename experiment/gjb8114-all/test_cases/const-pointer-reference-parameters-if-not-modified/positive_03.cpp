#include <cstddef>

std::size_t count_spaces(const char* text) {
    std::size_t count = 0;
    for (std::size_t i = 0; text[i] != 0; ++i) {
        if (text[i] == ' ') {
            ++count;
        }
    }
    return count;
}
