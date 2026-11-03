void func(int)
{
}

int main()
{
    int local = 0;
    (void)func(local); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
