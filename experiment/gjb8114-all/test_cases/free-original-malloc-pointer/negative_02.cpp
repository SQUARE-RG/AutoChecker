#include <cstdlib>

int main() {
    int* p = static_cast<int*>(std::calloc(3, sizeof(int)));
    if (p == nullptr) {
        return 1;
    }
    int* q = p + 1;
    std::free(q); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
