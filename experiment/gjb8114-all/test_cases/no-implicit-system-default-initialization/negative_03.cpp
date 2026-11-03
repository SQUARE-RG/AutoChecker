struct Counter {
    static inline int total; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-11-2]
};

int main() {
    Counter::total += 1;
    return 0;
}
