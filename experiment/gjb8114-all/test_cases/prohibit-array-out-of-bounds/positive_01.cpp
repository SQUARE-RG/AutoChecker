#include <cstddef>

void comp(int a[], int n)
{
    for (int i = 0; i < n; ++i)
    {
        a[i] = 0;
    }
}

int main()
{
    int array[100];
    comp(array, 100);
    return 0;
}
