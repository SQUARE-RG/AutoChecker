#include <iostream>

bool comes_first(const char* lhs, const char* rhs)
{
    if (*lhs <= *rhs)
    {
        return true;
    }
    return false;
}

int main()
{
    char letters[2] = {'a', 'b'};
    const char* first = &letters[0];
    const char* second = &letters[1];
    std::cout << comes_first(first, second) << '\n';
    return 0;
}
