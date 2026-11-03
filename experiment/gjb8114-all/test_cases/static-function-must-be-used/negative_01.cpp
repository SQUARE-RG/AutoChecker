static int compute_value(int data) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-13]
{
    return 2 * data;
}

int main()
{
    int input = 3;
    int result = 2 * input;
    return result == 6 ? 0 : 1;
}
