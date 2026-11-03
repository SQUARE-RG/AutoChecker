extern const int kLimit = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-19]

int main()
{
    return kLimit;
}
