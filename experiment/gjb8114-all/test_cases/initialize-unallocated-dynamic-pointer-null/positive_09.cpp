#include <cstdlib>

int main() {
    auto allocate = []() {
        int* p = nullptr;
        p = static_cast<int*>(std::malloc(sizeof(int)));
        if (p != nullptr) {
            *p = 42;
        } else {
            return -1;
        }
        std::free(p);
        return 0;
    };
    return allocate();
}
