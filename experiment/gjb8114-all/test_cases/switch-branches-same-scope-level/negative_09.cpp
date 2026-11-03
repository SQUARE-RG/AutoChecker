int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
        case 1:
            if (true)
            {
                case 2: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                    z = 1;
                    break;
            }
            break;
        default:
            z = 2;
            break;
    }
    return 0;
}
