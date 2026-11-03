int main() {
    int mask = 0;
    bool enabled = true;
    switch (((mask = 1) && enabled) ? 1 : 0) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-6-3]
        case 1:
            return 0;
        default:
            return 1;
    }
}
