int countdown(int start)
{
    int current = start;
    while (1 == 1) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-4]
    {
        if (current <= 0)
        {
            break;
        }
        --current;
    }
    return current;
}

int main()
{
    return countdown(3);
}
