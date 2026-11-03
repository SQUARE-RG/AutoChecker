int classify(int x)
{
    int value = 0;
    switch (x)
    {
        case 1: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
        case 2:
            value = 2;
            break;
        default:
            value = -1;
            break;
    }
    return value;
}
