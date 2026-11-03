int main() {
    if (int unusedValue = 42; true) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-8-2]
        return 0;
    }
    return 0;
}
