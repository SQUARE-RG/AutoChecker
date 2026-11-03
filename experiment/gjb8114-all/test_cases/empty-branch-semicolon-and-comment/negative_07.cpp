int main()
{
    int flag = 0;
    int value = 1;

    if (flag == 1)
    {
        value = 7;
    }
    else
    {
        // intentionally left empty
    } // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]

    return value;
}
