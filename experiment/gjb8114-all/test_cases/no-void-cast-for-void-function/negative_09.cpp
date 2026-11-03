void cleanup()
{
}

void finish()
{
    return (void)cleanup(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-12]
}

int main()
{
    finish();
    return 0;
}
