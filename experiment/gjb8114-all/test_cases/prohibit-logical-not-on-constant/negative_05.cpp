int main() {
    int result = 0;
    if (!'A') { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-10]
        result = 1;
    }
    return result;
}
