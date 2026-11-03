#include <cstdio>
#include <cstdlib>

int main() {
    long* values = static_cast<long*>(std::malloc(2 * sizeof(long)));
    if (values == nullptr) {
        return -1;
    }
    std::scanf("%ld", values + 1);
    return 0;
}
