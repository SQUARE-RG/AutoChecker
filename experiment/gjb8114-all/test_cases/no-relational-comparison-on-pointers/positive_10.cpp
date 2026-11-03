#include <algorithm>
#include <iostream>

int main()
{
    int left[] = {1, 2, 3};
    int right[] = {1, 2, 4};

    bool smaller = std::lexicographical_compare(left, left + 3, right, right + 3);

    if (smaller)
    {
        std::cout << "left is lexicographically smaller" << std::endl;
    }

    return 0;
}
