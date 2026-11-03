int identity(int value)
{
    return value;
}

int main()
{
    int x = 0;
    unsigned long size = sizeof(identity(x = 5)); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-13]
    return static_cast<int>(size);
}
