int main()
{
    bool result = !(42 - 42); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
    return result ? 0 : 1;
}
