int main()
{
    int x = 7;
    int y = 0;
    switch (static_cast<bool>(x)) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-4]
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
