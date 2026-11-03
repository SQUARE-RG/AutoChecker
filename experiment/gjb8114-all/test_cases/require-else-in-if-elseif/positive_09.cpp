#include <cstdlib>

int main() {
    int i = 0;
    int result = 0;
    while (i < 3) {
        if (i == 0) { result = 1; } else if (i == 1) { result = 2; } else { result = 3; }
        ++i;
    }
    return result;
}
