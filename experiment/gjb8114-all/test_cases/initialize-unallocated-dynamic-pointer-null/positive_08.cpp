#include <cstdlib>

int main() {
    using IntPtr = int*;
    IntPtr p = nullptr;
    p = static_cast<IntPtr>(std::aligned_alloc(alignof(int), sizeof(int)));
    if (p != nullptr) {
        *p = 7;
    }
    std::free(p);
    return 0;
}
