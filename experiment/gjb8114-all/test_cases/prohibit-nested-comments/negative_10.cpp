void process(int a, /* outer parameter comment
                      /* nested parameter comment
                   */ int b) // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
{
    (void)a;
    (void)b;
}

int main()
{
    process(1, 2);
    return 0;
}
