#include <iostream>
#include <cstddef>

int main()
{
    try
    {
        throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
    }
    catch (int)
    {
    }
    catch (const char *)
    {
    }
    return 0;
}
