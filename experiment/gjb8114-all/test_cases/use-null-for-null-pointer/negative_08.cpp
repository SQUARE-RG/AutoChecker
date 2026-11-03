#include <cstddef>
#include <cstdlib>

int main() {
    int value = 42;
    int* ptr = &value;
    int* selected = (value > 0) ? ptr : 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    if (selected == NULL) {
        return 0;
    }
    return 1;
}
