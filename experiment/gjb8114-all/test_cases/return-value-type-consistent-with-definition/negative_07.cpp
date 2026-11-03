short get_short(int value)
{
    return value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-10]
}

int main()
{
    int v = 42;
    short s = get_short(v);
    return static_cast<int>(s);
}
