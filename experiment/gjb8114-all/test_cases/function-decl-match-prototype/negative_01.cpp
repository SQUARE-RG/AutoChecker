int computeTotal(int value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-14]

int main()
{
    int amount = 20;
    int result = computeTotal(amount);
    return result == 30 ? 0 : 1;
}

int computeTotal(int number)
{
    return number + 10;
}
