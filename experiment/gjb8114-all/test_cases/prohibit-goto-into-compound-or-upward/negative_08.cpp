int main() {
    int x = 0;
start:
    x = x + 1;
    switch (x) {
    case 1:
        if (x < 5) {
            goto start; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
        }
        break;
    default:
        break;
    }
    return 0;
}
