int classify(int x)
{
    int value = 0;
    switch (x)
    {
        case 1:
            value = 1;
            break;
        case 2:
            value = 2;
            break;
        default: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
            value = -1;
    }
    return value;
}
