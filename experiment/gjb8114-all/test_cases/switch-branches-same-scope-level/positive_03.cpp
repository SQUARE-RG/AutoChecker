#include <cstdio>

int main(void)
{
    int x = 2;
    int z = 0;
    switch (x)
    {
        case 1:
            while (z < 1)
            {
                ++z;
            }
            break;
        case 2:
            z = 5;
            break;
        default:
            z = 7;
            break;
    }
    return z;
}
