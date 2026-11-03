#include <utility>

int value = 1;

int main()
{
    std::pair<int, int> p{2, 3};
    auto [value, other] = p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
    return value + other;
}
