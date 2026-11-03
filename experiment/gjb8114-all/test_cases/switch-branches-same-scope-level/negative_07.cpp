int main()
{
    int x = 2;
    int y = 1;
    int z = 0;

    switch (x)
    {
        case 1:
            z = 1;
            break;
        case 2:
            if (y)
                case 3: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                z = 3;
            break;
        default:
            z = 4;
            break;
    }

    return z;
}
