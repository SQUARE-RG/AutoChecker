#include <cstring>

int main()
{
    int src[4] = {1, 2, 3, 4};
    int des[2] = {0, 0};
    std::memcpy(des, src, sizeof(des));
    return 0;
}
