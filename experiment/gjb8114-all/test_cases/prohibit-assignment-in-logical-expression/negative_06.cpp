int main() {
    int state = 0;
    bool initialized = state > 0 || (state = 7); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
    return initialized ? 0 : 1;
}
