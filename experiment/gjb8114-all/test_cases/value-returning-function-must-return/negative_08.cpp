#include <vector>

int first_negative(const std::vector<int>& values)
{
    for (int value : values)
    {
        if (value < 0)
        {
            return value;
        }
    }
} // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-7]

int main()
{
    std::vector<int> values{-5, 2};
    return first_negative(values) + 5;
}
