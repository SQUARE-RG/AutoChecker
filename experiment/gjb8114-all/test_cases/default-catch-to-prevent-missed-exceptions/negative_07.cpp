#include <exception>
#include <iostream>
#include <stdexcept>

// noexcept 函数同样需要缺省捕获来防范未列出的异常
void parseNumber(int value) noexcept
{
    try {
        if (value < 0) {
            throw std::invalid_argument("negative value");
        }
        std::cout << "value=" << value << "\n";
    } catch (std::exception const& e) {  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-8-1]
        std::cout << "handled: " << e.what() << "\n";
    }
}

int main()
{
    parseNumber(5);
    parseNumber(-3);
    return 0;
}
