#include <cstdint>
#include <cstdlib>

int main()
{
    int* base = static_cast<int*>(std::malloc(3 * sizeof(int)));
    if (base == nullptr)
    {
        return 1;
    }

    base[0] = 10;
    base[1] = 20;
    base[2] = 30;

    std::uintptr_t address = reinterpret_cast<std::uintptr_t>(base);
    address += sizeof(int);
    std::free(reinterpret_cast<void*>(address)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-17]
    return 0;
}
