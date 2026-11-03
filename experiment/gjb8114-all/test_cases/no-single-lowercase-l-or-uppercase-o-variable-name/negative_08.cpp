int main()
{
    for (int O = 0; O < 1; ++O) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-11]
        return O;
    }
    return 0;
}
