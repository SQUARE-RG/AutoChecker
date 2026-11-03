#include <cstdint>

struct Data3
{
    unsigned long long a : 32;
    unsigned long long b : 32;
};

int main()
{
    Data3 d{};
    return static_cast<int>(d.a);
}
