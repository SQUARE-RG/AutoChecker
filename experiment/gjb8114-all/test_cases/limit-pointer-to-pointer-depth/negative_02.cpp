#include <cstddef>

void set_value(int*** out) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-1]
    *out = nullptr;
}

int main() {
    int value = 7;
    int* p = &value;
    int** pp = &p;

    set_value(&pp);
    return 0;
}
