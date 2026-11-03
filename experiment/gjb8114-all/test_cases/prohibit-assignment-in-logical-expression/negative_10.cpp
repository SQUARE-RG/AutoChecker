int main() {
    int i = 0;
    int n = 5;
    bool flag = false;
    while (i < n || (flag = (i < n))) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
        ++i;
    }
    return 0;
}
