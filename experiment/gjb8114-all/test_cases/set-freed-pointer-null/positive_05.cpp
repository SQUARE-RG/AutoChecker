#include <cstdlib>

int main() {
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr) {
        return 1;
    }
    *p = 42;
    auto release = [&p]() {
        std::free(p);
        p = nullptr;
    };
    release();
    return 0;
}
