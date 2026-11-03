// negative_05.cpp
int main() {
    int x = 1;
    int r = 0;
    goto L_inside;  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-5-1]
    switch (x) {
        case 1:
L_inside:
            r = 10;
            break;
        default:
            r = 20;
            break;
    }
    return r;
}
