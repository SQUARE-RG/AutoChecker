#include <cstring>

int main() {
    char destination[32];
    const char* source = "hello";
    std::strncpy(destination, source, sizeof(destination) - 1);
    destination[sizeof(destination) - 1] = '\0';
    return destination[0] == 'h' ? 0 : 1;
}
