void handle(int code)
{
    switch (code)
    {
        case 1:
            return;
        case 2:
            return;
        default:
            return;
    }
    int unreachable_value = code; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
}
