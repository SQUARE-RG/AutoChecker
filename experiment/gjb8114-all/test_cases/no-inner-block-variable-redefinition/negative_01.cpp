int main(void)
{
    int value = 1;
    int result = 0;
    if (value == 1)
    {
        int value = 2; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
        result = value * 3;
    }
    return result;
}
