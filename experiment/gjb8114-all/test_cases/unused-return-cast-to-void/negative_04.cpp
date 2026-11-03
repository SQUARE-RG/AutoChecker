#include <functional>

int compute(int value)
{
    return value + 1;
}

int main()
{
    std::function<int(int)> fn = compute;
    fn(4); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-11]
    return 0;
}
