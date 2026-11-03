#include <iostream>

int main()
{
    int arr[5] = {3, 1, 4, 1, 5};
    int maxValue = arr[0];

    for (int value : arr)
    {
        if (value > maxValue)
        {
            maxValue = value;
        }
    }

    std::cout << maxValue << '\n';
    return 0;
}
