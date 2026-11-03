void func(int para)
{
    para = para + 1;
}

int main()
{
    void (*fn)(int) = &func;
    (void)fn(7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    return 0;
}
