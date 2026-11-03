#include <string>

int main()
{
    char src[4] = {'a', 'b', 'c', 'd'};
    std::string s(src, src + sizeof(src));
    return 0;
}
