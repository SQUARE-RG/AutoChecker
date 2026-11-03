#include <array>

int main()
{
    std::array<int, 3> dest{};
    dest[3] = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-15]
    return 0;
}
