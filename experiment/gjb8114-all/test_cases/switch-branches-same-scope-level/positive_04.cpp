#include <cstdio>

int main(void)
{
    int x = 1;
    int y = 2;
    switch (x)
    {
        case 1:
            switch (y)
            {
                case 2:
                    x = 3;
                    break;
                default:
                    x = 4;
                    break;
            }
            break;
        default:
            x = 5;
            break;
    }
    return x;
}
