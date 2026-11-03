#include <cstddef>

int main()
{
    int value = 7;
    bool present = static_cast<bool>(&value);
    return 0;
}
