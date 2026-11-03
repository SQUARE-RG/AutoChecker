int main() {
    bool flag = false;
    while (flag < true) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-12-1]
        flag = true;
    }
    return 0;
}
