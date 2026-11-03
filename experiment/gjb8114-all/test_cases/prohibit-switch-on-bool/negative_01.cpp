int main(void)
{
    int x = 0;
    int y = 0;
    switch (0 == x) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
    {
        case 1:
            y = 1;
            break;
        default:
            y = 2;
            break;
    }
    return y;
}
