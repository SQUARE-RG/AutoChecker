#include <climits>

int adjust(int x)
{
    if (x < INT_MAX)
    {
        return x + 1;
    }
    else
    {
        return x - 1;
    }
}

int main()
{
    return adjust(0);
}
