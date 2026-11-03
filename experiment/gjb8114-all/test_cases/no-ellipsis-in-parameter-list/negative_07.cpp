int main()
{
    int (*fp)(int, ...) = nullptr; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-15]
    (void)fp;
    return 0;
}
