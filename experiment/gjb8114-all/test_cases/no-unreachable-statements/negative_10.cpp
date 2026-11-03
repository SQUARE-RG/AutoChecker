#include <exception>

void stop_now()
{
    std::terminate();
    int after_terminate = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
}
