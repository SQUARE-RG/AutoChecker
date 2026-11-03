int main() {
    int x = 3;
    int y = 0;
    switch (x) {
        case 1:
            y = 1;
            break;
        case 2:
            while (y == 0) {
                case 3: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                    y = 3;
                    break;
            }
            break;
        default:
            y = 4;
            break;
    }
    return y;
}
