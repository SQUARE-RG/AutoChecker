int main()
{
    volatile unsigned int v = 1;
    switch (v + v) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-13]
    {
    case 2:
        return 0;
    default:
        break;
    }
    return 1;
}
