#include <cstdlib>

int main() {
    int value = 5;
    int* ptr = &value;
    bool flag{ptr != nullptr};
    return flag ? EXIT_SUCCESS : EXIT_FAILURE;
}
