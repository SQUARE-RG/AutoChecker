int main() {
    int count;
    while (count > 0) // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    {
        count = 1;
    }
    return 0;
}
