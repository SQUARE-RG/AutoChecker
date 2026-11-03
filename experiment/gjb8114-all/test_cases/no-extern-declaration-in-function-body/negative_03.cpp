int values[3] = {1, 2, 3};

int sum_values()
{
    extern int values[]; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    return values[0] + values[1] + values[2];
}

int main()
{
    return sum_values();
}
