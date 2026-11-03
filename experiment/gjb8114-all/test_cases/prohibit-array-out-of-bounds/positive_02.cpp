#include <iostream>

int main()
{
    int arr[10] = {0};
    int x;
    std::cin >> x;
    int idx = (x * 3 + 7) / 2;
    if (idx >= 0 && idx < 10)
    {
        arr[idx] = 1;
    }
    return 0;
}
