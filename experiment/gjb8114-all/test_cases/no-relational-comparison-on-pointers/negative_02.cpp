int main()
{
    int values[2] = {1, 2};
    int *p = &values[0];
    int *q = &values[1];
    int result = 0;

    if (p < q) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-2]
    {
        result = *p;
    }
    else
    {
        result = *q;
    }

    return result;
}
