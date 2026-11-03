#include <iostream>

struct MyError
{
    int code;
};

int main()
{
    try
    {
        throw MyError{42};
    }
    catch (MyError e)
    {
        std::cout << e.code << std::endl;
    }
    return 0;
}
