int selectValue(int value)
{
    switch (value)
    {
        case 0:
            return 100;
        default: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
            value = -1;
        case 2:
            return value;
    }
    return 0;
}
