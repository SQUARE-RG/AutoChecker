#include <cstdlib>
#include <cstddef>
#include <memory>

int main()
{
    void* raw = std::malloc(64);
    if (raw == nullptr)
    {
        return -1;
    }

    void* cursor = static_cast<char*>(raw) + 1;
    std::size_t space = 63;
    void* aligned = std::align(16, sizeof(int), cursor, space);
    if (aligned == nullptr)
    {
        std::free(raw);
        return -1;
    }

    *static_cast<int*>(aligned) = 7;
    std::free(raw);
    return 0;
}
