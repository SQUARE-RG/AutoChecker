#include <cstddef>
#include <cstring>

void copy_message(char* destination, const char* source, std::size_t capacity) {
    if (capacity == 0) {
        return;
    }
    std::strncpy(destination, source, capacity - 1);
    destination[capacity - 1] = '\0';
}

int main() {
    char buffer[16];
    copy_message(buffer, "hello", sizeof(buffer));
    return buffer[0] == 'h' ? 0 : 1;
}
