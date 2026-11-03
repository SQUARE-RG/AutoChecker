int negativeIndex()
{
    return -1;
}

int main()
{
    int data[3] = {0, 0, 0};
    data[negativeIndex()] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
    return 0;
}
