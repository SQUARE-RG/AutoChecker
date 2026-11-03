int lookup(int key)
{
    int total = 0;
    switch (key)
    {
        case 1: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-7]
            for (int i = 0; i < key; ++i)
            {
                if (total > 100)
                {
                    break;
                }
                total += i;
            }
        case 2:
            total += 2;
            break;
        default:
            total = -1;
            break;
    }
    return total;
}

int main()
{
    return lookup(1);
}
