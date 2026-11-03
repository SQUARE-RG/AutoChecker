int sumArray(int values[], int count); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int main()
{
    int values[3] = {1, 2, 3};
    return sumArray(values, 3) == 6 ? 0 : 1;
}

int sumArray(int data[], int count)
{
    int total = 0;
    for (int i = 0; i < count; ++i)
        total += data[i];
    return total;
}
