#include <cstdint>

int main()
{
    unsigned int value = 0;
    unsigned int* ptr = &value;
    bool flag = static_cast<bool>(ptr);
    (void)flag;
    return 0;
}
