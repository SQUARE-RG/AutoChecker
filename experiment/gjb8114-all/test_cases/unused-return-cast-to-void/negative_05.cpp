#include <functional>

int compute_value(int input)
{
    return input + 1;
}

int main()
{
    std::invoke(compute_value, 41); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
