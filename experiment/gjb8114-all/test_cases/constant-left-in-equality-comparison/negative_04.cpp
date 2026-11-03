int main() {
    double ratio = 1.5;
    if (ratio != 1.5) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-12-1]
        return 1;
    }
    return 0;
}
