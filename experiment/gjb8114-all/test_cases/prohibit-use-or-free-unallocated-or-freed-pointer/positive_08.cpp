#include <cstdlib>

int main() {
    int *p = static_cast<int *>(std::malloc(sizeof(int)));
    if (p == nullptr) {
        return 0;
    }
    *p = 7;
    int *q = static_cast<int *>(std::realloc(p, 2 * sizeof(int)));
    if (q == nullptr) {
        std::free(p);
        return 0;
    }
    q[0] = 7;
    q[1] = 9;
    int sum = q[0] + q[1];
    std::free(q);
    q = nullptr;
    return sum;
}
