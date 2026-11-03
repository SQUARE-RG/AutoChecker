#include <cstdint>

int main() {
    int value = 3;
    int* p = &value;
    int* q = (int*)p;
    const int* cq = (const int*)q;
    long width = (long)value;
    int result = static_cast<int>(width);
    return result;
}
