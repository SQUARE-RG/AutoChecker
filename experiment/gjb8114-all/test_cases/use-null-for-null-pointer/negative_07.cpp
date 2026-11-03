#include <cstddef>
#include <cstdlib>

int main() {
    int value = 5;
    int* ptr = &value;
    if (ptr == 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
        return 1;
    }
    return 0;
}
