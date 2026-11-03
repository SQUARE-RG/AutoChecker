#include <cstddef>
#include <iostream>

int main()
{
    try
    {
        throw 42;
    }
    catch (int)
    {
        // 在 catch 处理块内部直接抛出 NULL 字面量
        throw NULL; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-5]
    }
    return 0;
}
