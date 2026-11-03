int sign = 0;
int main()
{
    int local = 0;
    int sign = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-1]
    return local + sign;
}
