#include <type_traits>

int main()
{
    int a = 37;
    int r = a % std::integral_constant<int, 0>::value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-12]
    return r;
}
