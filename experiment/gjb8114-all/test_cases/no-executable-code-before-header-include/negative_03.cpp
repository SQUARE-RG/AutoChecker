int runtime_value();

int global_value = runtime_value();

#include <ciso646> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

int runtime_value()
{
    return 3;
}

int main()
{
    return global_value;
}
