#include <cstdlib>
#include <iostream>

int main()
{
    int* p = static_cast<int*>(std::malloc(sizeof(int)));

    std::cin >> *p; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-3-8]

    std::cout << *p << '\n';
    std::free(p);
    return 0;
}
