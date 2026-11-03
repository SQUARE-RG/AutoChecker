int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
    case 1:
        {
            case 3: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                z = 3;
        }
        break;
    case 2:
        z = 2;
        break;
    default:
        z = 0;
        break;
    }
    return 0;
}
