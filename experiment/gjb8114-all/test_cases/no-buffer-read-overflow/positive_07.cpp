#include <string>
#include <iostream>

int main()
{
    char buffer[4] = {'a', 'b', 'c', 'd'};
    std::string text(buffer, sizeof(buffer));
    std::cout << text.size();
    return 0;
}
