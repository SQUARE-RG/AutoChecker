#include <memory>

int main()
{
    std::allocator<int> alloc;
    int* ptr = alloc.allocate(1);
    *ptr = 7;

    alloc.deallocate(ptr, 1);

    int result = *ptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    (void)result;
    return 0;
}
