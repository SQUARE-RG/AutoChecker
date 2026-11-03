#include <algorithm>

int main()
{
    int src[3] = {1, 2, 3};
    int des[5] = {0, 0, 0, 0, 0};
    std::copy(src, src + 3, des);
    return 0;
}
