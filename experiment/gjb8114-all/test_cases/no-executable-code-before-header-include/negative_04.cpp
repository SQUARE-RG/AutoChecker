struct RuntimeInit
{
    RuntimeInit();
};

RuntimeInit global_object;

#include <ciso646> // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-3]

RuntimeInit::RuntimeInit()
{
}

int main()
{
    return 0;
}
