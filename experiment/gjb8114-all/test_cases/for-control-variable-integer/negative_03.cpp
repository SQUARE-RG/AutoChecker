int main()
{
    int values[5] = {1, 2, 3, 4, 5};
    int sum = 0;
    for (int* p = values; p != values + 5; ++p) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-9-2]
    {
        sum += *p;
    }
    return sum;
}
