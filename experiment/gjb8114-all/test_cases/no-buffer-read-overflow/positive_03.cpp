#include <cstring>

int main()
{
    int src[2] = {1, 2};
    int des[4] = {0, 0, 0, 0};
    std::memmove(des, src, sizeof(src));
    return 0;
}
