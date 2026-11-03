#include <cstdlib>

struct Holder {
    int* p = nullptr;

    Holder() {
        p = static_cast<int*>(std::malloc(sizeof(int)));
    }

    ~Holder() {
        std::free(p);
    }
};

int main() {
    Holder h;
    if (h.p != nullptr) {
        *h.p = 1;
    }
    return 0;
}
