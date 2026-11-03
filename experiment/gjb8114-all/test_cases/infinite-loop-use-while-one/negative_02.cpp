int drain(int value)
{
    // CHECK-MESSAGES: :[[@LINE+1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    for (;;)
    {
        if (value <= 0)
        {
            return 0;
        }
        value -= 1;
    }
}

int main(void)
{
    return drain(3);
}
