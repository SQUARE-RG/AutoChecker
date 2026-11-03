#include <cstring>

int main()
{
    char buffer[8] = {0};
    std::memset(buffer, 0, sizeof(buffer));
    return 0;
}
