#include <algorithm>

int main()
{
    int src[4] = {1, 2, 3, 4};
    int dst[2] = {0, 0};
    std::copy_n(src, 2, dst);
    return 0;
}
