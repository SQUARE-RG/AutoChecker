#include <iostream>

struct Status
{
    bool ready;
};

int main()
{
    Status status{true};
    int result = 0;
    switch (status.ready) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
    {
        case true:
            result = 1;
            break;
        default:
            result = 2;
            break;
    }
    std::cout << result << '\n';
    return 0;
}
