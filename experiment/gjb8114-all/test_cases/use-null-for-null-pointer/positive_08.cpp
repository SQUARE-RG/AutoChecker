#include <cstddef>
#include <cstdlib>

int main() {
    int value = 42;
    int* ptr = &value;
    int* selected = (value > 0) ? ptr : NULL;
    if (selected == NULL) {
        return 0;
    }
    return 1;
}
