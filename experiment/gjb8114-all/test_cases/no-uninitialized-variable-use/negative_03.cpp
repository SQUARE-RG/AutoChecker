static int increment(int value) {
    return value + 1;
}

int main() {
    int value;
    int result;
    result = increment(value); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-1]
    return result;
}
