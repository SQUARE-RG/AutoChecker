#include <iostream>

int main()
{
    int flag = 0;

    auto spin = [&flag]() -> int
    {
        for(;;) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
        {
            if (flag != 0)
            {
                return flag;
            }
            ++flag;
        }
    };

    return spin();
}
