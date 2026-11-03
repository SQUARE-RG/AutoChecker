#include <cstdlib>
#include <iostream>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));
    if (p == nullptr)
    {
        return -1;
    }

    std::cin >> *p;
    std::cout << *p << '\n';
    std::free(p);
    return 0;
}
