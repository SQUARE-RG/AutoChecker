int negative_04(int n)
{
    int sum = 0;
    for (int i = 0; i < n; ++i) {
        continue;
        sum += i; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-8-1]
    }
    return sum;
}

int main()
{
    return negative_04(5);
}
