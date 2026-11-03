#include <iostream>
#include <memory>

int main()
{
    std::unique_ptr<int> owner(new int(7));
    int* raw = owner.get();
    owner.reset();
    int value = *raw; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-16]
    std::cout << value << '\n';
    return 0;
}
