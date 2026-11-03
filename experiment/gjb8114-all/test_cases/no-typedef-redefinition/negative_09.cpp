typedef int mytype;

int main()
{
    for (typedef float mytype; ; )
    // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
    {
        mytype x = 1.0;
        (void)x;
        break;
    }
    return 0;
}
