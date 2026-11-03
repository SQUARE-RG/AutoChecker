int main() {
    int state = 2;
    switch (state) {
        case 2: {
            int state = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-7]
            ++state;
            break;
        }
        default:
            break;
    }
    return state;
}
