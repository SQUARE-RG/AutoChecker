int main()
{
    auto l = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
    l = 0;
    return 0;
}
