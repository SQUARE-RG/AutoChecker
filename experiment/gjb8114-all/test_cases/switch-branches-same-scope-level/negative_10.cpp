int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
        case 1:
            if (false)
                z = 1;
            else
                case 2: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                    z = 2;
            break;
        default:
            z = 3;
            break;
    }
    return 0;
}
