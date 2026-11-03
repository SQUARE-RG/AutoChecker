#include <cstddef>
#include <iostream>

int main() {
    auto strlen = [](const char* text) -> std::size_t {
        std::size_t count = 0;
        while (text[count] != '\0') {
            ++count;
        }
        return count;
    };

    std::size_t length = strlen("hello");
    std::cout << length << '\n';
    return length == 5 ? 0 : 1;
}
