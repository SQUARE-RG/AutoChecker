void tick()
{
}

int main()
{
    for (int i = 0; i < 3; (void)tick(), ++i) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
    {
    }
    return 0;
}
