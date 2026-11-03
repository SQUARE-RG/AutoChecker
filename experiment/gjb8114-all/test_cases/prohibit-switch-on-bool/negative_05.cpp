int main()
{
    int x = 5;
    int y = 0;
    switch ((x > 0) ? true : false) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
    {
        case true:
            y = 1;
            break;
        case false:
            y = 2;
            break;
    }
    return y;
}
