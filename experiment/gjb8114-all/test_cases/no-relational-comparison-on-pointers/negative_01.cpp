int fsub(int *a, int *b)
{
    int sub = 0;
    if (a > b) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
    {
        sub = (*a) - (*b);
    }
    else
    {
        sub = (*b) - (*a);
    }
    return sub;
}

int main()
{
    int a = 1;
    int b = 2;
    int sub = fsub(&a, &b);
    return sub;
}
