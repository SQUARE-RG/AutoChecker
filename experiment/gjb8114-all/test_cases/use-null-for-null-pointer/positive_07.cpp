#include <cstddef>
#include <cstdlib>

int main() {
    int value = 5;
    int* ptr = &value;
    if (ptr == NULL) {
        return 1;
    }
    return 0;
}
