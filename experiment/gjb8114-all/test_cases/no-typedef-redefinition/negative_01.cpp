typedef int mytype;

int main()
{
    typedef float mytype; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-3]
    mytype x = 1.0f;
    (void)x;
    return 0;
}
