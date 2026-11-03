#include <stdexcept>

int error_code = 0;

int main()
{
    try {
        throw std::runtime_error("boom");
    } catch (const std::runtime_error& error_code) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
        (void)error_code;
        return 1;
    }
}
