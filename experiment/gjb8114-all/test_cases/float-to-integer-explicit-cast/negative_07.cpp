int main()
{
    char ch = 0;
    double value = 3.75;
    ch = value; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-10-1]
    return ch;
}
