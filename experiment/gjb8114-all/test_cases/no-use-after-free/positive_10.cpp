#include <memory>

int main()
{
    std::allocator<int> alloc;
    int* ptr = alloc.allocate(1);
    *ptr = 7;

    int result = *ptr;
    (void)result;

    alloc.deallocate(ptr, 1);
    return 0;
}
