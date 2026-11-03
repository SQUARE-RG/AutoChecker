#include <iostream>
#include <string>

int main()
{
    std::string *msg = new std::string("boom");
    try
    {
        throw msg;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-2]
    }
    catch (std::string *p)
    {
        std::cout << *p << std::endl;
        delete p;
    }
    return 0;
}
