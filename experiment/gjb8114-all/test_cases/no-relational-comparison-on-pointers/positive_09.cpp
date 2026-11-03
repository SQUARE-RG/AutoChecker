#include <cstddef>
#include <iostream>
#include <iterator>

int main()
{
    int values[] = {10, 20, 30, 40};
    int* first = values;
    int* last = values + 4;
    std::ptrdiff_t span = std::distance(first, last);

    if (span > 2)
    {
        std::cout << "span is greater than two" << std::endl;
    }

    return 0;
}
