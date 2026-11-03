int main()
{
    int O = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
    O = 1;
    return O;
}
