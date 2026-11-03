#include <cstddef>
#include <iostream>

const char *lookup()
{
    return NULL;
}

int main()
{
    try
    {
        // 抛出的是函数调用结果，未在 throw 处直接写出 NULL 字面量
        throw lookup();
    }
    catch (const char *)
    {
        std::cout << "caught" << std::endl;
    }
    return 0;
}
