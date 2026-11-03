int main()
{
    int x = 2;
    int z = 0;
    switch (x)
    {
    case 1:
        do
        {
            case 4: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                z = 4;
                break;
        } while (false);
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
