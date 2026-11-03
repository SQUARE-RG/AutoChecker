int accumulate(int selector)
{
    int total = 0;
    for (int i = 0; i < 2; ++i)
    {
        switch (selector)
        {
            case 0: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
                total += 1;
                continue;
            default:
                total += 2;
                break;
        }
        total += 3;
    }
    return total;
}
