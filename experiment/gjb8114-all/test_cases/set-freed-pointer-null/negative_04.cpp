#include <cstdlib>

struct Holder {
    int* data;
};

int main() {
    Holder h;
    h.data = static_cast<int*>(std::malloc(sizeof(int)));
    if (h.data == nullptr) {
        return 1;
    }
    *h.data = 7;
    std::free(h.data); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-6]
    return 0;
}
