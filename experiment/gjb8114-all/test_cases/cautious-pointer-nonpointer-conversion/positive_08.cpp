#include <cstdint>

int main() {
    int value = 4;
    double d = double(value);
    long width = long(d);
    int* p = &value;
    int* q = reinterpret_cast<int*>(p);
    const int* cq = static_cast<const int*>(q);
    return static_cast<int>(width);
}
