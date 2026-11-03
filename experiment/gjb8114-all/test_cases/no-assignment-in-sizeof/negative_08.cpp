int main()
{
    int x = 1;
    int *p = &x;
    auto ilen = sizeof(*p = x); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    (void)ilen;
    return 0;
}
