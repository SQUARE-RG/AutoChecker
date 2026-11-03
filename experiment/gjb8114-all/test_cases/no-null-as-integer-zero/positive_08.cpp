#include <cstdlib>

int scale(int factor = 0);

int main()
{
    int result = scale();
    return result;
}

int scale(int factor)
{
    return factor * 2;
}
