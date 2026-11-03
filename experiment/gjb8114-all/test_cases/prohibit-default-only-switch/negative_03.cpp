int main()
{
    int value = 0;
    switch (value)
    {
        default:
        {
            value += 1;
            break;
        }
    } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
    return value;
}
