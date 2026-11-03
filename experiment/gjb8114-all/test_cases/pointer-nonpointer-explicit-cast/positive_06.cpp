#include <cstddef>

int main()
{
    unsigned int value = 1U;
    unsigned int* ptr = &value;
    std::nullptr_t non_pointer = nullptr;
    ptr = static_cast<unsigned int*>(non_pointer);
    (void)value;
    (void)ptr;
    return 0;
}
