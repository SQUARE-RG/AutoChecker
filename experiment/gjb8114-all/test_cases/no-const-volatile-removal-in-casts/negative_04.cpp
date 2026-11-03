#include <iostream>

int main() {
    const int value = 42;
    const int& cref = value;
    int& ref = const_cast<int&>(cref); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-5-2]
    ref = 43;
    std::cout << value << '\n';
    return 0;
}
