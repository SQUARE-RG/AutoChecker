#include <array>
#include <cstring>

int main() {
    std::array<char, 16> destination{};
    const char* source = "widget";
    std::strncpy(destination.data(), source, destination.size() - 1);
    destination[destination.size() - 1] = '\0';
    return destination[0] == 'w' ? 0 : 1;
}
