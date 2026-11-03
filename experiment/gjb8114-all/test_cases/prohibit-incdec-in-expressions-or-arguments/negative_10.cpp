int main() {
    int remaining = 3;
    if (--remaining > 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-5]
        return remaining;
    }
    return 0;
}
