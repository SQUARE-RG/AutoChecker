#include <iostream>

bool is_positive(int value) noexcept
{
    return value > 0;
}

int main()
{
    int result = 0;
    switch (noexcept(is_positive(1))) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
    {
        case true:
            result = 1;
            break;
        case false:
            result = 2;
            break;
    }
    std::cout << result << '\n';
    return 0;
}
