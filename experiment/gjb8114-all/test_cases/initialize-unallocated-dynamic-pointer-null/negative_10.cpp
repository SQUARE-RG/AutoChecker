#include <cstdlib>

int main() {
    int** pp; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-7]
    pp = static_cast<int**>(std::malloc(sizeof(int*)));
    if (pp != nullptr) {
        *pp = nullptr;
    } else {
        return -1;
    }
    std::free(pp);
    return 0;
}
