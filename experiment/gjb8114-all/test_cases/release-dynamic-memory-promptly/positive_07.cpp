#include <cstdlib>
#include <cstring>
#include <iostream>

int main() {
    char* buffer = static_cast<char*>(std::malloc(16));
    if (!buffer) {
        return 1;
    }
    std::strcpy(buffer, "hello");
    char* grown = static_cast<char*>(std::realloc(buffer, 64));
    if (!grown) {
        std::free(buffer);
        return 1;
    }
    std::strcat(grown, " world");
    std::cout << grown << '\n';
    std::free(grown);
    return 0;
}
