#include <cstddef>

int sum_elements(const int arr[], int n)
{
    int total = 0;
    for (int i = 0; i < n; ++i) {
        total += arr[i];
    }
    return total;
}
