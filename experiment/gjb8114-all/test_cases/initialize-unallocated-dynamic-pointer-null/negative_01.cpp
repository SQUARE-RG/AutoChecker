#include <cstdlib>

int main() {
    int *value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    value = static_cast<int *>(std::malloc(sizeof(int)));
    if (value != nullptr) {
        *value = 1;
        std::free(value);
    } else {
        return -1;
    }
    return 0;
}
