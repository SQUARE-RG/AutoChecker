#include <cstddef>

struct Holder {
    int* ptr;
    int value;
};

int main() {
    int value = 7;
    Holder holder = { 0, value }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    return holder.ptr == NULL ? 0 : 1;
}
