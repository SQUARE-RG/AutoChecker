int main() {
    int mode = 1;
    switch (mode) {
        case 1: {
            register int value = 42; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-1-13-2]
            (void)value;
            break;
        }
        default:
            break;
    }
    return 0;
}
