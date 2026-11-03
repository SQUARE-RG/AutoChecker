int main()
{
    int value = 0;
    if ((value = 1, value > 0)) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-6-6]
        return 0;
    }
    return 1;
}
