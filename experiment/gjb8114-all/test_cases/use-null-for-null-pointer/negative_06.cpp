#include <cstddef>

void reset(int* ptr = 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
{
    if (ptr != NULL) {
        *ptr = 0;
    }
}

int main()
{
    int value = 7;
    reset(&value);
    return 0;
}
