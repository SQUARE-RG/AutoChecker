// positive_05.cpp
#include <iostream>

#define PRINT_SCOPE(msg) { std::cout << msg << '\n'; }

int main()
{
    PRINT_SCOPE("hello");
    PRINT_SCOPE("world");
    return 0;
}
