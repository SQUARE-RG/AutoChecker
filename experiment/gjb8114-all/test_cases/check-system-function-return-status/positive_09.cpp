#include <cstdio>

int main() {
    const char* path = "stale-file.txt";
    if (std::remove(path) != 0) {
        return 1;
    }
    return 0;
}
