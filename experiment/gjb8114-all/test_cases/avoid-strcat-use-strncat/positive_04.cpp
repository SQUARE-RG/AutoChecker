#include <cstring>
#include <cstddef>

int main() {
    char buffer[32] = "abc";
    using std::strncat;
    std::size_t room = sizeof(buffer) - std::strlen(buffer) - 1;
    strncat(buffer, "def", room);
    return 0;
}
