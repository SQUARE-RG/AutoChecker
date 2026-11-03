#include <cstdlib>

int main()
{
    int* arr = static_cast<int*>(std::malloc(4 * sizeof(int)));
    if (arr == nullptr)
    {
        return 1;
    }

    arr[0] = 7;
    std::free(arr);
    return 0;
}
