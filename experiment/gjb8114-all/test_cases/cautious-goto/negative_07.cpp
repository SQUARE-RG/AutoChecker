#include <iostream>

int main() {
    int value = 3;
    goto adjust;
    // CHECK-MESSAGES: :[[@LINE-1]]:5: warning: avoid using 'goto' for flow control [ucassaat-a-1-5-1]
    {
adjust:
        value += 1;
    }
    std::cout << value << '\n';
    return 0;
}
