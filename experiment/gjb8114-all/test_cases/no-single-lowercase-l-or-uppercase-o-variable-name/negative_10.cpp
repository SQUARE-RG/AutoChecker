int main()
{
    int values[] = {1, 2, 3};
    for (int l : values) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
    {
        if (l == 2)
        {
            return 0;
        }
    }
    return 1;
}
