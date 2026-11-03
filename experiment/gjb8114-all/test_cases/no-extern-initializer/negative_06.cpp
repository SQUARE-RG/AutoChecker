#include <string>

extern std::string greeting("hello"); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main(void)
{
    greeting += " world";
    return greeting.empty() ? 1 : 0;
}
