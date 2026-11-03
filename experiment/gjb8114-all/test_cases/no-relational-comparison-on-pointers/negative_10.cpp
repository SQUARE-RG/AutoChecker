#include <algorithm>
#include <vector>

int main()
{
    int values[] = {30, 10, 20};
    std::vector<int*> elements{&values[0], &values[1], &values[2]};

    auto byAddress = [](int* lhs, int* rhs) { return lhs < rhs; }; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]

    std::sort(elements.begin(), elements.end(), byAddress);
    return 0;
}
