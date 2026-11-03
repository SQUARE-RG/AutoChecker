int compute(int code)
{
    int value = 0;
    switch (code)
    {
        case 1: /*shared*/
        case 2: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
        case 3:
            value = 10;
            break;
        case 4:
            value = 20;
            break;
        default:
            value = -1;
            break;
    }
    return value;
}

int main()
{
    return compute(1);
}
