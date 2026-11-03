#include <utility>

void compute(void)
{
}

int main()
{
    auto [compute, value] = std::pair<int, int>{0, 1}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-3]
    (void)value;
    return compute;
}
