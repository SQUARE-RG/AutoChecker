#include <cstddef>

int main()
{
    unsigned int value = 1U;
    unsigned int* ptr = &value;
    std::nullptr_t non_pointer = nullptr;
    ptr = non_pointer; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-5]
    (void)value;
    (void)ptr;
    return 0;
}
