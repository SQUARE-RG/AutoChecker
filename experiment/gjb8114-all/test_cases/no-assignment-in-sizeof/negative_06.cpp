#include <iostream>

struct S
{
    int field;
};

int main()
{
    S obj{0};
    std::size_t ilen = sizeof(obj.field = 7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    std::cout << ilen << std::endl;
    return 0;
}
