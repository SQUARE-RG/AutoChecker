#include <cstddef>
#include <cstdlib>

int main() {
    int* x = static_cast<int*>(std::malloc(sizeof(int)));
    if (x != 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
    {
        *x = 1;
    } else {
        return -1;
    }
    std::free(x);
    return 0;
}
