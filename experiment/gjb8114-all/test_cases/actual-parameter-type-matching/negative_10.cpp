void process(int value, int extra = 0)
{
    (void)value;
    (void)extra;
}

int main()
{
    short small = 3;
    process(small); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-7-2]
    return 0;
}
