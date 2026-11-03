#include <cstddef>

int* locate(int* candidate)
{
    if (candidate != NULL) {
        return candidate;
    }
    return 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-9]
}

int main()
{
    int value = 42;
    int* found = locate(&value);
    return (found != NULL) ? 0 : 1;
}
