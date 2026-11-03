#include <cstdlib>

int find_first_negative(const int *values, int count)
{
    for (int i = 0; i < count; ++i)
    {
        if (values[i] < 0)
        {
            return i;
        }
    }
    return -1;
}

int main(void)
{
    int data[4] = {3, 5, -2, 7};
    return find_first_negative(data, 4) + 2;
}
