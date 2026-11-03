int main() {
    int value = 1;
    switch (value) { default: break; } // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-5]
    return 0;
}
