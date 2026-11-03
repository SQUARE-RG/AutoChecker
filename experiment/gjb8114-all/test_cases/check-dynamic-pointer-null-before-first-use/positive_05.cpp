#include <cstdlib>
#include <cstring>

int main() {
    char *buffer = static_cast<char *>(std::malloc(32));
    if (buffer == nullptr) {
        return -1;
    }
    std::strcpy(buffer, "hello");
    std::free(buffer);
    return 0;
}
