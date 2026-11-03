#include <cstddef>
#include <iostream>

int main()
{
    try
    {
        auto f = []() -> void
        {
            throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
        };
        f();
    }
    catch (const char *)
    {
        std::cout << "caught" << std::endl;
    }
    return 0;
}
