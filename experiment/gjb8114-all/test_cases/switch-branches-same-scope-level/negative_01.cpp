int main() {
    int x = 2;
    int y = 0;
    int z = 0;
    switch (x) {
        case 1:
            if (y == 0) {
                z = 2;
                break;
            }
            break;
        case 2:
            z = 1;
            break;
        default:
        {
            case 3: // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-4-8]
                z = 3;
                break;
        }
    }
    return z;
}
