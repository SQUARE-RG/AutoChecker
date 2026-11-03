#include <vector>

int firstValue(const std::vector<int>& values)
{
    for (int value : values)
        return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-1]
    return -1;
}

int main()
{
    std::vector<int> data{4, 5, 6};
    return firstValue(data);
}
