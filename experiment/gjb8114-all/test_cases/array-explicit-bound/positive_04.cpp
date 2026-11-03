#include <cstring>

int main()
{
    char greeting[6] = "hello";
    return std::strlen(greeting) == 5 ? 0 : 1;
}
