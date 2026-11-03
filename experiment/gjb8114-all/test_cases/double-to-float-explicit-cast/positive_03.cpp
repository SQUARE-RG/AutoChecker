#include <iostream>

double getValue()
{
    return 3.5;
}

int main()
{
    float fValue;
    fValue = static_cast<float>(getValue());
    std::cout << fValue << std::endl;
    return 0;
}
