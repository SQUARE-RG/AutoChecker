#include <cstdint>
#include <cstdlib>

int main()
{
    int* base = static_cast<int*>(std::malloc(2 * sizeof(int)));
    if (base == nullptr)
    {
        return 1;
    }

    base[0] = 1;
    base[1] = 2;

    std::uintptr_t original_address = reinterpret_cast<std::uintptr_t>(base);
    std::free(reinterpret_cast<void*>(original_address));
    return 0;
}
