int main(void)
{
    int state = 0;

    // CHECK-MESSAGES: :[[@LINE+1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    for(;;)
    {
        if (1 == state)
        {
            break;
        }
        ++state;
    }
    return 0;
}
