#include <new>

int main() {
    int *p = new (std::nothrow) int[6];
    if (!p) {
        return 1;
    }
    p[0] = 1;
    p[5] = 6;
    delete[] p;
    return 0;
}
