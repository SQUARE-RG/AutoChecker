int main() {
    int flag = 1;
    int result = 0;
    if (flag == 1) {
        result = 2;
    } else {
        /* no deal with */
        // CHECK-MESSAGES: :[[@LINE-1]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-2]
    }
    return result;
}
