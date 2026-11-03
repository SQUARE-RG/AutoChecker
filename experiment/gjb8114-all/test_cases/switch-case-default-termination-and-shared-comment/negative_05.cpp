int compute(int value)
{
    int result = 0;
    switch (value)
    {
        case 1: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
            if (value > 0)
            {
                result = 10;
                break;
            }
            result = 20;
        case 2:
            result = 30;
            break;
        default:
            result = -1;
            break;
    }
    return result;
}

int main()
{
    return compute(1);
}
