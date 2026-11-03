const int kGlobalLimit = 100;

int clampValue(int value) {
    extern const int kGlobalLimit; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-1-17]
    if (value > kGlobalLimit) {
        return kGlobalLimit;
    }
    return value;
}
