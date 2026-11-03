#include <cstdlib>

struct Holder {
    int* p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]

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
