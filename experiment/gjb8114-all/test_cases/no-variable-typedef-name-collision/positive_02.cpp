#include <array>
#include <iostream>

typedef std::array<int, 3> Triple;

int sumTriple(const Triple& values)
{
    return values[0] + values[1] + values[2];
}

int main()
{
    Triple composite = {1, 2, 3};
    std::cout << sumTriple(composite) << std::endl;
    return 0;
}
