int main()
{
    int i = 0;
    int j = 0;
    if (i = !1) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
        j = 1;
    }
    return 0;
}
