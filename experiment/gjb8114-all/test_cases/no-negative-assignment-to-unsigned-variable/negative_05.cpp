typedef unsigned int UInt;

int main()
{
    UInt value;
    value = -20; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-15]
    return 0;
}
