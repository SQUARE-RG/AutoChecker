#include <cstddef>
#include <iostream>

struct NullPtrException
{
    const char *message;
};

int main()
{
    NullPtrException e{NULL};
    try
    {
        // 抛出的是异常对象而非 NULL 字面量本身
        throw e;
    }
    catch (const NullPtrException &ex)
    {
        std::cout << "caught exception object" << std::endl;
    }
    return 0;
}
