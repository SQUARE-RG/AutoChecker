unsigned int get_value(int flag);

int main()
{
    unsigned int result = get_value(1);
    return static_cast<int>(result);
}

unsigned int get_value(int flag)
{
    int value = -7;
    if (flag == 1)
    {
        return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
    }
    return 0u;
}
