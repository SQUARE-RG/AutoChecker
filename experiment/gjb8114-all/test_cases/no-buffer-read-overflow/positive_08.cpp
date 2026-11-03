#include <vector>
#include <iostream>

int main()
{
    int src[2] = {1, 2};
    std::vector<int> values;
    values.insert(values.end(), src, src + 2);
    std::cout << values.size();
    return 0;
}
