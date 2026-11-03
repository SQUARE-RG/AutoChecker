int main()
{
    int* values = new int[]{0, 1, 2}; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-18]
    int sum = 0;
    for (int i = 0; i < 3; ++i)
    {
        sum += values[i];
    }
    delete[] values;
    return sum;
}
