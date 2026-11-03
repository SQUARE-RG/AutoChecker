#include <iostream>

bool toggle(bool value)
{
    return value ? false : true;
}

int main()
{
    bool outReg1 = true;
    bool outReg2 = false;
    bool flag = toggle(outReg1);

    if (flag)
    {
        std::cout << "flag set\n";
    }

    if (outReg2)
    {
        std::cout << "outReg2 set\n";
    }

    return 0;
}
