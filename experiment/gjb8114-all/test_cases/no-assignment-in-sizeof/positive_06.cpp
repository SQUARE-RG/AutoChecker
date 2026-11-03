#include <iostream>

struct S
{
    int field;
};

int main()
{
    S obj{0};
    obj.field = 7;
    std::size_t ilen = sizeof(obj.field);
    std::cout << ilen << std::endl;
    return 0;
}
