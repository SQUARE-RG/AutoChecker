int main() {
    int value = 0;
    int result = value + 1; /* tail /* nested */ // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-2-6]
    return result;
}
