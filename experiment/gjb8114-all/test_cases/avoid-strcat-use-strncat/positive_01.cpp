#include <cstring>

int main() {
    char message[64] = "hello";
    const char* suffix = " world";
    std::strncat(message, suffix, sizeof(message) - std::strlen(message) - 1);
    return 0;
}
