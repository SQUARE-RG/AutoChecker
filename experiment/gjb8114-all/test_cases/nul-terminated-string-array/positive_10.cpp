#include <cstdio>
#include <vector>

int main()
{
    std::vector<char> buf{'y', 'e', 's'};
    buf.push_back('\0');
    std::printf("%s\n", buf.data());
    return 0;
}
