#include <array>
#include <iostream>

int main()
{
    std::array<bool, 4> flags{true, false, true, false};
    int count = 0;

    for (bool flag : flags)
    {
        if (flag)
        {
            ++count;
        }
    }

    std::cout << count << '\n';
    return 0;
}
