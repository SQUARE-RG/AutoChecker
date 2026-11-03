void process(unsigned int endl) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-4]
{
    (void)endl;
}

int main()
{
    process(1U);
    return 0;
}
