void writeWithDefault(int index = -1)
{
    int data[3] = {0, 0, 0};
    data[index] = 1; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-9]
}

int main()
{
    writeWithDefault();
    return 0;
}
