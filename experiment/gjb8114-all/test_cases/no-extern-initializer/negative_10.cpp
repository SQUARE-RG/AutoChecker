int identity(int v)
{
    return v;
}

extern int (*handler)(int) = identity; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main()
{
    return handler(1);
}
