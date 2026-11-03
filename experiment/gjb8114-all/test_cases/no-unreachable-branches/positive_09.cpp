#include <cstdint>

int branch_on_zero(unsigned int value)
{
    if (value == 0u)
    {
        return 0;
    }
    else
    {
        return 1;
    }
}

int main()
{
    return branch_on_zero(0u) + branch_on_zero(1u);
}
